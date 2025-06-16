"""Tests for the terminal manager."""

import time
import unittest
from unittest.mock import MagicMock, patch

from terminal_mcp_server.terminal_manager import TerminalManager, TerminalSession


class TestTerminalSession(unittest.TestCase):
    """Test the TerminalSession class."""

    @patch("pexpect.spawn")
    def test_init(self, mock_spawn):
        """Test initialization of a terminal session."""
        # Setup
        mock_process = MagicMock()
        mock_spawn.return_value = mock_process
        
        # Execute
        session = TerminalSession("echo hello", timeout=10)
        
        # Assert
        mock_spawn.assert_called_once()
        self.assertEqual(session.command, "echo hello")
        self.assertEqual(session.timeout, 10)
        self.assertEqual(session.process, mock_process)
        self.assertEqual(session.output_buffer, "")
        self.assertIsNone(session.exit_code)
    
    @patch("pexpect.spawn")
    def test_send_input(self, mock_spawn):
        """Test sending input to a terminal session."""
        # Setup
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_process.before = "output after input"
        mock_spawn.return_value = mock_process
        
        # Execute
        session = TerminalSession("bash")
        output = session.send_input("echo hello")
        
        # Assert
        mock_process.sendline.assert_called_once_with("echo hello")
        mock_process.expect.assert_called_once()
        self.assertEqual(output, "output after input")
        self.assertEqual(session.output_buffer, "output after input")
    
    @patch("pexpect.spawn")
    def test_get_output(self, mock_spawn):
        """Test getting output from a terminal session."""
        # Setup
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_process.before = "some output"
        mock_spawn.return_value = mock_process
        
        # Execute
        session = TerminalSession("bash")
        output = session.get_output()
        
        # Assert
        mock_process.expect.assert_called_once()
        self.assertEqual(output, "some output")
        self.assertEqual(session.output_buffer, "some output")
    
    @patch("pexpect.spawn")
    def test_is_running(self, mock_spawn):
        """Test checking if a terminal session is running."""
        # Setup
        mock_process = MagicMock()
        mock_process.isalive.return_value = True
        mock_spawn.return_value = mock_process
        
        # Execute
        session = TerminalSession("bash")
        running = session.is_running()
        
        # Assert
        mock_process.isalive.assert_called_once()
        self.assertTrue(running)
    
    @patch("pexpect.spawn")
    def test_terminate(self, mock_spawn):
        """Test terminating a terminal session."""
        # Setup
        mock_process = MagicMock()
        mock_process.isalive.side_effect = [True, False]  # First call returns True, second call returns False
        mock_spawn.return_value = mock_process
        
        # Execute
        session = TerminalSession("bash")
        session.terminate()
        
        # Assert
        mock_process.terminate.assert_called_once_with(force=False)


class TestTerminalManager(unittest.TestCase):
    """Test the TerminalManager class."""

    def test_generate_session_id(self):
        """Test generating a session ID."""
        # Setup
        manager = TerminalManager()
        
        # Execute
        session_id = manager.generate_session_id()
        
        # Assert
        self.assertIsInstance(session_id, str)
        self.assertTrue(len(session_id) > 0)
    
    @patch("terminal_mcp_server.terminal_manager.TerminalSession")
    def test_run_command(self, mock_terminal_session):
        """Test running a command."""
        # Setup
        mock_session = MagicMock()
        mock_session.get_output.return_value = "command output"
        mock_session.exit_code = None
        mock_session.is_running.return_value = True
        mock_terminal_session.return_value = mock_session
        
        manager = TerminalManager()
        
        # Execute
        output, exit_code, running = manager.run_command("echo hello", "test-session")
        
        # Assert
        mock_terminal_session.assert_called_once_with("echo hello", 30)
        self.assertEqual(output, "command output")
        self.assertIsNone(exit_code)
        self.assertTrue(running)
        self.assertIn("test-session", manager.sessions)
    
    @patch("terminal_mcp_server.terminal_manager.TerminalSession")
    def test_send_input(self, mock_terminal_session):
        """Test sending input to a session."""
        # Setup
        mock_session = MagicMock()
        mock_session.send_input.return_value = "input output"
        mock_session.exit_code = None
        mock_session.is_running.return_value = True
        mock_terminal_session.return_value = mock_session
        
        manager = TerminalManager()
        manager.sessions["test-session"] = mock_session
        
        # Execute
        output, exit_code, running = manager.send_input("test-session", "echo hello")
        
        # Assert
        mock_session.send_input.assert_called_once_with("echo hello")
        self.assertEqual(output, "input output")
        self.assertIsNone(exit_code)
        self.assertTrue(running)
    
    @patch("terminal_mcp_server.terminal_manager.TerminalSession")
    def test_get_session_state(self, mock_terminal_session):
        """Test getting the state of a session."""
        # Setup
        mock_session = MagicMock()
        mock_session.get_output.return_value = "current output"
        mock_session.exit_code = None
        mock_session.is_running.return_value = True
        mock_terminal_session.return_value = mock_session
        
        manager = TerminalManager()
        manager.sessions["test-session"] = mock_session
        
        # Execute
        output, exit_code, running = manager.get_session_state("test-session")
        
        # Assert
        mock_session.get_output.assert_called_once()
        self.assertEqual(output, "current output")
        self.assertIsNone(exit_code)
        self.assertTrue(running)
    
    @patch("terminal_mcp_server.terminal_manager.TerminalSession")
    def test_terminate_session(self, mock_terminal_session):
        """Test terminating a session."""
        # Setup
        mock_session = MagicMock()
        mock_terminal_session.return_value = mock_session
        
        manager = TerminalManager()
        manager.sessions["test-session"] = mock_session
        
        # Execute
        manager.terminate_session("test-session")
        
        # Assert
        mock_session.terminate.assert_called_once()
        self.assertNotIn("test-session", manager.sessions)
    
    @patch("terminal_mcp_server.terminal_manager.TerminalSession")
    def test_list_sessions(self, mock_terminal_session):
        """Test listing sessions."""
        # Setup
        mock_session = MagicMock()
        mock_terminal_session.return_value = mock_session
        
        manager = TerminalManager()
        manager.sessions["test-session-1"] = mock_session
        manager.sessions["test-session-2"] = mock_session
        
        # Execute
        sessions = manager.list_sessions()
        
        # Assert
        self.assertEqual(len(sessions), 2)
        self.assertIn("test-session-1", sessions)
        self.assertIn("test-session-2", sessions)
