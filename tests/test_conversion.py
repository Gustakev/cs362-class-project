"""
Author: Sam Daughtry
Date: 2026-02-22
Description: Tests the conversion feature.
"""

import unittest
from unittest.mock import patch, MagicMock
from functional_components.conversion_engine.app.convert_file import convert_proprietary_file_format

class TestConversion(unittest.TestCase):
    @patch('functional_components.conversion_engine.app.convert_file.Image.open')
    @patch('functional_components.conversion_engine.app.convert_file.conversion_temp_store.store_in_directory')
    @patch('functional_components.conversion_engine.app.convert_file.converted_asset')
    def test_convert_heic_success(self, mock_converted_asset, mock_store_in_directory, mock_image_open):
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        mock_store_in_directory.return_value = 'conversions/test.png'
        
        convert_proprietary_file_format('test.heic')
        
        mock_image_open.assert_called_once_with('test.heic')
        mock_image.save.assert_called_once_with('test.png')
        mock_store_in_directory.assert_called_once_with('test.png')
        mock_converted_asset.success = True
        mock_converted_asset.filepath = 'conversions/test.png'

    @patch('functional_components.conversion_engine.app.convert_file.VideoFileClip')
    @patch('functional_components.conversion_engine.app.convert_file.conversion_temp_store.store_in_directory')
    @patch('functional_components.conversion_engine.app.convert_file.converted_asset')
    def test_convert_mov_success(self, mock_converted_asset, mock_store_in_directory, mock_video_clip):

        mock_video = MagicMock()
        mock_video_clip.return_value = mock_video
        mock_store_in_directory.return_value = 'conversions/test.mp4'
        
        convert_proprietary_file_format('test.mov')
        
        mock_video_clip.assert_called_once_with('test.mov')
        mock_video.write_videofile.assert_called_once_with('test.mp4', codec='libx264')
        mock_store_in_directory.assert_called_once_with('test.mp4')
        mock_converted_asset.success = True
        mock_converted_asset.filepath = 'conversions/test.mp4'

if __name__ == '__main__':
    unittest.main()