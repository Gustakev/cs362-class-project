"""
Author: Sam Daughtry (Edited by Kevin Gustafson)
Date: 2026-02-23
Description: Conversion engine for transforming proprietary media formats
    into standard formats. The main entry point is `convert_asset`, which
    accepts an AssetToConvert object and returns a ConvertedAsset describing
    either a successful conversion or an error.
"""

from functional_components.conversion_engine.domain.asset_to_convert import (
    AssetToConvert,
)

from functional_components.conversion_engine.domain.converted_asset import (
    ConvertedAsset,
)

from functional_components.conversion_engine.data.media_converter import (
    convert_image,
    convert_video,
)


def convert_asset(asset_to_convert: AssetToConvert, temp_dir=None) -> ConvertedAsset:
    """Convert an asset based on the rules in the convert_type_dict."""
    asset = asset_to_convert.asset_to_convert
    convert_map = asset_to_convert.convert_type_dict

    ext = asset.file_extension.upper()

    if ext not in convert_map:
        return ConvertedAsset(
            success=False,
            error=f"No conversion rule for extension: {ext}",
        )

    target_format = convert_map[ext]
    source_path = asset.backup_relative_path

    try:
        if ext in ("HEIC", "HEIF"):
            output_file = convert_image(source_path, target_format, temp_dir)
        elif ext == "MOV":
            output_file = convert_video(source_path, target_format, temp_dir)
        else:
            return ConvertedAsset(
                success=False,
                error=f"Unsupported conversion type: {ext}",
            )

        converted = asset.model_copy(
            update={"backup_relative_path": output_file}
        )

        return ConvertedAsset(success=True, converted_asset=converted)

    except Exception as e:
        return ConvertedAsset(success=False, error=str(e))
    