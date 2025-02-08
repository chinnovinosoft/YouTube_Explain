import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.io.path import ObjectStoragePath

# Define S3 bucket and connection
BUCKET_NAME = "praveen-airflow-bucket-1"
AWS_CONN_ID = "aws_default"
BASE_PATH = f"s3://{BUCKET_NAME}/airflow_stuff/"

# Define the DAG
with DAG(
    dag_id="object_storage",
    start_date=pendulum.datetime(2025, 2, 8, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["object-storage", "s3"],
) as dag:

    # Initialize the base S3 path
    base = ObjectStoragePath(BASE_PATH, conn_id=AWS_CONN_ID)

    @task
    def create_folder():
        """Create a folder inside the S3 bucket."""
        folder_path = base / "new_folder/"
        folder_path.mkdir(parents=True, exist_ok=True)
        return str(folder_path)

    @task
    def list_files() -> list:
        """List all files and folders in the given S3 bucket path."""
        return [str(f) for f in base.iterdir()]

    @task
    def create_file() -> ObjectStoragePath:
        """Create a new file path in S3."""
        return base / "new_folder/data.txt"

    @task
    def write_file(path: ObjectStoragePath):
        """Write data to a new file in S3."""
        with path.open("wb") as f:
            f.write(b"Hello, Object Storage! I am writing from Airflow!!")

    @task
    def read_file(path: ObjectStoragePath) -> str:
        """Read content from a file in S3."""
        with path.open() as f:
            return f.read()

    @task
    def copy_file(src_path: ObjectStoragePath) -> ObjectStoragePath:
        """Copy a file from one S3 location to another."""
        dest_path = base / "new_folder1/copy_of_data.txt"
        # Ensure that the destination folder exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.copy(dest_path)
        return dest_path

    @task
    def move_file(src_path: ObjectStoragePath) -> ObjectStoragePath:
        """Move (rename) a file in S3."""
        dest_path = base / "new_folder2/moved_data.txt"
        # Ensure that the destination folder exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.rename(dest_path)
        return dest_path

    @task
    def delete_file(path: ObjectStoragePath):
        """Delete a file in S3."""
        path.unlink(missing_ok=True)

    # DAG dependencies
    folder = create_folder()
    files = list_files()
    new_file = create_file()

    write = write_file(new_file)
    read = read_file(new_file)

    copy = copy_file(new_file)
    move = move_file(copy)

    delete_file(move)  # Deletes the moved file after operations

    # Define task dependencies
    folder >> new_file
    new_file >> write >> read
    read >> copy >> move >> delete_file(move)
