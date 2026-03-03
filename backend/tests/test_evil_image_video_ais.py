#!/usr/bin/env python3
"""
Backend API Tests for LuciferOS - Evil Image & Video AIs
Tests the new 14 Evil Image/Video Generating AIs and video engine
"""

import pytest
import requests
import os
import sys

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://demon-companion.preview.emergentagent.com')

# Add tools path for direct testing
sys.path.insert(0, '/app/tools')


class TestEvilImageVideoAIs:
    """Test the 14 new Evil Image & Video Generating AIs"""
    
    # List of new Evil Image/Video AIs
    EVIL_AIS = [
        'darkflux', 'nightmareai', 'demoncanvas', 'lewdgpt', 'goreartist',
        'deepfakeai', 'videodevil', 'snuffgpt', 'propagandaai', 'biohazardai',
        'warcrimesai', 'cosmichorror', 'druglordia', 'animatordark'
    ]
    
    def test_total_ai_count_is_88(self):
        """Verify total AI count is 88"""
        from lilith_ai_engine import DarkLLMProvider
        modes = DarkLLMProvider.list_providers()
        assert len(modes) == 88, f"Expected 88 AIs, got {len(modes)}"
    
    def test_all_evil_ais_exist(self):
        """Verify all 14 Evil Image/Video AIs exist in DarkLLMProvider"""
        from lilith_ai_engine import DarkLLMProvider
        modes = DarkLLMProvider.list_providers()
        
        for ai in self.EVIL_AIS:
            assert ai in modes, f"Evil AI '{ai}' not found in providers"
    
    def test_evil_ai_has_correct_structure(self):
        """Verify Evil AIs have correct structure with name, description, system_prompt"""
        from lilith_ai_engine import DarkLLMProvider
        
        for ai in self.EVIL_AIS:
            provider = DarkLLMProvider.get_provider(ai)
            assert provider is not None, f"Provider '{ai}' returned None"
            assert 'name' in provider, f"Provider '{ai}' missing 'name'"
            assert 'description' in provider, f"Provider '{ai}' missing 'description'"
            assert 'system_prompt' in provider, f"Provider '{ai}' missing 'system_prompt'"
            assert 'capabilities' in provider, f"Provider '{ai}' missing 'capabilities'"
    
    def test_set_mode_to_darkflux(self):
        """Test setting AI mode to DarkFlux via API"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/set-mode",
            json={"mode": "darkflux"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['provider']['name'] == 'DarkFlux'
    
    def test_set_mode_to_nightmareai(self):
        """Test setting AI mode to NightmareAI via API"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/set-mode",
            json={"mode": "nightmareai"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['provider']['name'] == 'NightmareAI'
    
    def test_set_mode_to_videodevil(self):
        """Test setting AI mode to VideoDevil via API"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/set-mode",
            json={"mode": "videodevil"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['provider']['name'] == 'VideoDevil'
    
    def test_reset_mode_to_lilith(self):
        """Reset mode back to LILITH after tests"""
        response = requests.post(
            f"{BASE_URL}/_dash/ai/set-mode",
            json={"mode": "lilith"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True


class TestVideoEngine:
    """Test the FREE video generation engine"""
    
    def test_video_engine_exists(self):
        """Verify LilithFreeVideoEngine class exists"""
        from lilith_free_engines import LilithFreeVideoEngine
        engine = LilithFreeVideoEngine()
        assert engine is not None
    
    def test_video_styles_available(self):
        """Verify video styles are available"""
        from lilith_free_engines import LilithFreeVideoEngine
        engine = LilithFreeVideoEngine()
        styles = engine.list_styles()
        
        assert len(styles) >= 7, f"Expected at least 7 video styles, got {len(styles)}"
        
        # Check for expected styles
        expected_styles = ['horror', 'cyberpunk', 'demon', 'gore', 'nsfw', 'nightmare', 'apocalypse']
        for style in expected_styles:
            assert style in styles, f"Video style '{style}' not found"
    
    def test_video_style_has_prefix(self):
        """Verify each video style has a prompt prefix"""
        from lilith_free_engines import LilithFreeVideoEngine
        engine = LilithFreeVideoEngine()
        styles = engine.list_styles()
        
        for style_name, prefix in styles.items():
            if style_name != 'normal':
                assert len(prefix) > 10, f"Style '{style_name}' has too short prefix"


class TestTelegramBotIntegration:
    """Test Telegram bot has video commands"""
    
    def test_telegram_bot_file_exists(self):
        """Verify Telegram bot file exists"""
        import os
        bot_path = '/app/telegram_lilith_bot_v6.py'
        assert os.path.exists(bot_path), f"Telegram bot file not found at {bot_path}"
    
    def test_telegram_bot_has_video_command(self):
        """Verify Telegram bot has /video command handler"""
        with open('/app/telegram_lilith_bot_v6.py', 'r') as f:
            content = f.read()
        
        assert 'generate_video' in content, "generate_video function not found in bot"
        assert '/video' in content or 'video' in content, "/video command not found in bot"
    
    def test_telegram_bot_has_videostyles_command(self):
        """Verify Telegram bot has /videostyles command handler"""
        with open('/app/telegram_lilith_bot_v6.py', 'r') as f:
            content = f.read()
        
        assert 'list_video_styles' in content, "list_video_styles function not found in bot"


class TestDashboardDropdown:
    """Test dashboard has Evil Image & Video AIs in dropdown"""
    
    def test_dashboard_has_evil_ai_optgroup(self):
        """Verify dashboard HTML has Evil Image & Video AIs optgroup"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        
        # Check for the optgroup label
        assert 'EVIL IMAGE & VIDEO AIs' in response.text, "Evil Image & Video AIs optgroup not found"
    
    def test_dashboard_has_darkflux_option(self):
        """Verify dashboard has DarkFlux option"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert 'darkflux' in response.text, "darkflux option not found in dashboard"
        assert 'DarkFlux' in response.text, "DarkFlux label not found in dashboard"
    
    def test_dashboard_has_videodevil_option(self):
        """Verify dashboard has VideoDevil option"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert 'videodevil' in response.text, "videodevil option not found in dashboard"
        assert 'VideoDevil' in response.text, "VideoDevil label not found in dashboard"
    
    def test_dashboard_shows_88_ais(self):
        """Verify dashboard shows 88 AIs in dropdown label"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert '88 AIs' in response.text, "88 AIs label not found in dashboard"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
