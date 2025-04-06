import sqlite3

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project.paths import get_project_assets_directory


def project_asset_exists_fs(asset_type: AssetType, asset_id: str) -> bool:
    if get_data_from_db(asset_id):
        return True
    else:
        return (get_project_assets_directory(asset_type) / f"{asset_id}.toml").exists()


def get_data_from_db(asset_id) -> bool:
    conn = sqlite3.connect('local_db_AIConsole.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM asset_info WHERE id = ?', (asset_id,))
        table = cursor.fetchone()

        if table:
            return True
    except sqlite3.Error as e:
        conn.close()
    finally:
        conn.close()
    return False
