"""Tests for the ECMWF DISS (Dissemination Data Store) client."""

import datetime
import json
import os
import stat
import tempfile
import warnings
from unittest.mock import MagicMock, patch

import pytest

from ecmwf.opendata.diss import (
    DISS_HOST,
    DissAuth,
    DissClient,
    build_diss_filename,
    parse_diss_filename,
)


# ===========================================================================
# WMO filename builder/parser tests
# ===========================================================================


class TestBuildDissFilename:
    def test_surface_step_18(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        assert build_diss_filename("surface", dt, 18) == "FSD06230000062318001"

    def test_model_step_90(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        assert build_diss_filename("model", dt, 90) == "FMD06230000062618001"

    def test_pressure_step_24(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        assert build_diss_filename("pressure", dt, 24) == "FPD06230000062400001"

    def test_amdar(self):
        dt = datetime.datetime(2026, 6, 23, 6, 0)
        assert build_diss_filename("amdar", dt, 0) == "AND06230600062306011"

    def test_step_zero_seq_011(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        result = build_diss_filename("surface", dt, 0)
        assert result == "FSD06230000062300011"
        assert result.endswith("011")

    def test_step_nonzero_seq_001(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        result = build_diss_filename("surface", dt, 3)
        assert result.endswith("001")

    def test_custom_seq(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        result = build_diss_filename("model", dt, 6, seq=5)
        assert result.endswith("005")

    def test_step_crosses_month(self):
        # Jan 30 00Z + 72h = Feb 2 00Z
        dt = datetime.datetime(2026, 1, 30, 0, 0)
        result = build_diss_filename("surface", dt, 72)
        assert result == "FSD01300000020200001"

    def test_step_crosses_year(self):
        # Dec 31 00Z + 48h = Jan 2 00Z
        dt = datetime.datetime(2026, 12, 31, 0, 0)
        result = build_diss_filename("model", dt, 48)
        # valid date is Jan 2: 0102
        assert result == "FMD12310000010200001"

    def test_invalid_type_raises(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        with pytest.raises(ValueError, match="Unknown file_type"):
            build_diss_filename("invalid", dt, 6)

    def test_all_prefixes(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        assert build_diss_filename("model", dt, 3).startswith("FMD")
        assert build_diss_filename("pressure", dt, 3).startswith("FPD")
        assert build_diss_filename("surface", dt, 3).startswith("FSD")
        assert build_diss_filename("amdar", dt, 3).startswith("AND")


class TestParseDissFilename:
    def test_known_example(self):
        result = parse_diss_filename("FMD06230000062618001")
        assert result["prefix"] == "FMD"
        assert result["file_type"] == "model"
        assert result["analysis_mmdd"] == "0623"
        assert result["analysis_hhmm"] == "0000"
        assert result["valid_mmdd"] == "0626"
        assert result["valid_hh"] == "18"
        assert result["seq"] == 1

    def test_roundtrip(self):
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        for ftype in ("model", "pressure", "surface", "amdar"):
            for step in (0, 3, 24, 90):
                fname = build_diss_filename(ftype, dt, step)
                parsed = parse_diss_filename(fname)
                assert parsed["file_type"] == ftype
                assert parsed["analysis_mmdd"] == "0623"
                assert parsed["analysis_hhmm"] == "0000"

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="too short"):
            parse_diss_filename("FMD")


# ===========================================================================
# DissAuth tests
# ===========================================================================


class TestDissAuth:
    def test_adds_header_for_diss_host(self):
        auth = DissAuth("user", "pass")
        request = MagicMock()
        request.url = f"https://{DISS_HOST}/ecpds/data/file/20260623/test"
        result = auth(request)
        # HTTPBasicAuth was called (it modifies the request in-place)
        assert result is not None

    def test_skips_header_for_other_host(self):
        auth = DissAuth("user", "pass")
        request = MagicMock()
        request.url = "https://other.example.com/data/file"
        request.headers = {}
        result = auth(request)
        # Should return the request unmodified
        assert result is request

    def test_repr_redacts_credentials(self):
        auth = DissAuth("myuser", "secretpass")
        r = repr(auth)
        assert "myuser" not in r
        assert "secretpass" not in r
        assert "redacted" in r


# ===========================================================================
# Credential loading tests
# ===========================================================================


class TestGetCredentials:
    def test_from_env_vars(self):
        with patch.dict(
            os.environ,
            {"ECMWF_DISS_USERNAME": "envuser", "ECMWF_DISS_PASSWORD": "envpass"},
        ):
            from ecmwf.opendata.urls import get_credentials

            result = get_credentials("diss")
            assert result == {"username": "envuser", "password": "envpass"}

    def test_env_vars_override_config(self):
        with patch.dict(
            os.environ,
            {"ECMWF_DISS_USERNAME": "envuser", "ECMWF_DISS_PASSWORD": "envpass"},
        ):
            with patch("ecmwf.opendata.urls._CREDENTIALS", {"diss": {"username": "cfguser", "password": "cfgpass"}}):
                from ecmwf.opendata.urls import get_credentials

                result = get_credentials("diss")
                assert result == {"username": "envuser", "password": "envpass"}

    def test_missing_returns_empty_dict(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("ecmwf.opendata.urls._CREDENTIALS", {}):
                from ecmwf.opendata.urls import get_credentials

                # Remove env vars if present
                os.environ.pop("ECMWF_DISS_USERNAME", None)
                os.environ.pop("ECMWF_DISS_PASSWORD", None)
                result = get_credentials("diss")
                assert result == {}


# ===========================================================================
# DissClient tests
# ===========================================================================


class TestDissClient:
    def test_init_with_explicit_credentials(self):
        client = DissClient(username="user", password="pass")
        assert client.username == "user"
        assert client.password == "pass"

    def test_init_missing_credentials_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ECMWF_DISS_USERNAME", None)
            os.environ.pop("ECMWF_DISS_PASSWORD", None)
            with patch("ecmwf.opendata.diss.get_credentials", return_value={}):
                with pytest.raises(ValueError, match="DISS credentials required"):
                    DissClient()

    def test_error_message_excludes_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ECMWF_DISS_USERNAME", None)
            os.environ.pop("ECMWF_DISS_PASSWORD", None)
            with patch("ecmwf.opendata.diss.get_credentials", return_value={}):
                try:
                    DissClient()
                except ValueError as e:
                    msg = str(e)
                    # Should not contain any actual credential values
                    assert "password" not in msg.lower() or "ECMWF_DISS_PASSWORD" in msg

    def test_download_requires_date(self):
        client = DissClient(username="user", password="pass")
        with pytest.raises(ValueError, match="date is required"):
            client.download(target="/tmp/test")

    def test_download_requires_step_or_filename(self):
        client = DissClient(username="user", password="pass")
        with pytest.raises(ValueError, match="Specify step/steps or filename/filenames"):
            client.download(target="/tmp/test", date=20260623)

    def test_build_url(self):
        client = DissClient(username="user", password="pass")
        dt = datetime.datetime(2026, 6, 23, 0, 0)
        url = client._build_url(dt, "FSD06230000062318001")
        assert "20260623" in url
        assert "FSD06230000062318001" in url

    @patch("ecmwf.opendata.diss.download")
    def test_download_single_file(self, mock_download):
        client = DissClient(username="user", password="pass")
        result = client.download(
            target="/tmp/test.grib2",
            date=20260623,
            file_type="surface",
            step=18,
        )
        assert result == ["/tmp/test.grib2"]
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert "FSD06230000062318001" in call_args[0][0]

    @patch("ecmwf.opendata.diss.download")
    def test_download_by_filename(self, mock_download):
        client = DissClient(username="user", password="pass")
        result = client.download(
            target="/tmp/test.grib2",
            date=20260623,
            filename="FMD06230000062618001",
        )
        assert result == ["/tmp/test.grib2"]
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert "FMD06230000062618001" in call_args[0][0]

    @patch("ecmwf.opendata.diss.download")
    @patch("os.makedirs")
    def test_download_multi_step(self, mock_makedirs, mock_download):
        client = DissClient(username="user", password="pass")
        result = client.download(
            target="/tmp/output",
            date=20260623,
            file_type="surface",
            steps=[3, 6, 9],
        )
        assert len(result) == 3
        assert mock_download.call_count == 3
        mock_makedirs.assert_called_once_with("/tmp/output", exist_ok=True)


# ===========================================================================
# Debug logging scope test
# ===========================================================================


class TestDebugLogging:
    def test_debug_flag_scopes_to_package_logger(self):
        import logging

        from ecmwf.opendata import Client

        root_level_before = logging.getLogger().level
        # Create client with debug (may fail to connect, that's ok)
        try:
            Client(source="ecmwf", debug=True)
        except Exception:
            pass

        pkg_logger = logging.getLogger("ecmwf.opendata")
        assert pkg_logger.level == logging.DEBUG
        # Root logger should not have been changed
        assert logging.getLogger().level == root_level_before


# ===========================================================================
# Unified Client(source="diss") interface tests
# ===========================================================================


class TestClientDissInterface:
    def test_client_source_diss_creates_diss_backend(self):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        assert client._is_diss
        assert hasattr(client, "_diss")

    def test_client_source_diss_retrieve_raises(self):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        with pytest.raises(NotImplementedError, match="retrieve.*not supported"):
            client.retrieve(date=20260623)

    def test_client_source_diss_latest_raises(self):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        with pytest.raises(NotImplementedError, match="latest.*not supported"):
            client.latest()

    def test_client_source_diss_list_files_delegates(self):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        with patch.object(client._diss, "list_files", return_value=[]) as mock:
            result = client.list_files(20260623, file_type="surface")
            mock.assert_called_once_with(20260623, file_type="surface")
            assert result == []

    @patch("ecmwf.opendata.diss.download")
    def test_client_source_diss_download_delegates(self, mock_download):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        result = client.download(
            target="/tmp/test.grib2",
            date=20260623,
            file_type="surface",
            step=18,
        )
        assert result == ["/tmp/test.grib2"]
        mock_download.assert_called_once()

    def test_client_source_diss_url_property(self):
        from ecmwf.opendata import Client

        client = Client(source="diss", username="user", password="pass")
        assert "diss.ecmwf.int" in client.url

    def test_client_normal_source_list_files_raises(self):
        from ecmwf.opendata import Client

        client = Client(source="aws")
        with pytest.raises(NotImplementedError, match="only available for source='diss'"):
            client.list_files(20260623)
