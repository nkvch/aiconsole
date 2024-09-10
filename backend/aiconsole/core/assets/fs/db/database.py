import psycopg2


class MaterialsService:
    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost", port=5432, database="materials", user="aiconsole", password="aiconsole"
        )

    def __del__(self):
        if self.connection:
            self.connection.close()

    def get_file(self, project_id: str, file_name: str) -> str | None:
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       SELECT file_contents
                       FROM materials
                       WHERE project_id = %s AND file_name = %s
                       """,
            (project_id, file_name),
        )

        result = cursor.fetchone()

        if result is None:
            return None
        else:
            return bytes(result[0]).decode("utf-8")

    def add_file(self, project_id: str, file_name: str, file_contents: str):
        existing_file = self.get_file(project_id, file_name)

        if existing_file is not None:
            raise MaterialAlreadyExistsError(f"Material: {file_name} already exists in Project: {project_id}")

        cursor = self.connection.cursor()

        cursor.execute(
            """
                       INSERT INTO materials (project_id, file_name, file_contents)
                       VALUES (%s, %s, %s)
                       """,
            (project_id, file_name, psycopg2.Binary(file_contents.encode("utf-8"))),
        )

        self.connection.commit()

        cursor.close()

    def edit_file(self, project_id, file_name, new_file_contents, new_file_name):
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       UPDATE materials
                       SET file_contents = %s, file_name = %s
                       WHERE file_name = %s AND project_id = %s
                       """,
            (psycopg2.Binary(new_file_contents.encode("utf-8")), new_file_name, file_name, project_id),
        )

        self.connection.commit()

        cursor.close()

    def delete_file(
        self,
        project_id,
        file_name,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       DELETE FROM materials
                       WHERE project_id = %s AND file_name = %s
                       """,
            (project_id, file_name),
        )

        self.connection.commit()

        cursor.close()

    def get_all_file_names(self, project_id: str) -> list[str]:
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       SELECT file_name
                       FROM materials
                       WHERE project_id = %s
                       """,
            (project_id,),
        )

        results = cursor.fetchall()

        file_names = [row[0] for row in results]

        return file_names

    def get_all_files(self, project_id) -> list[tuple[str, str]]:
        cursor = self.connection.cursor()

        cursor.execute(
            """
                       SELECT file_name, file_contents
                       FROM materials
                       WHERE project_id = %s
                       """,
            (project_id,),
        )

        results = cursor.fetchall()

        files = [(str(row[0]), bytes(row[1]).decode("utf-8")) for row in results]

        return files


class MaterialNotFoundError(Exception):
    """Exception raised when a material is not found in the database."""

    pass


class MaterialAlreadyExistsError(Exception):
    """Exception raised when trying to create a material that already exists."""

    pass
