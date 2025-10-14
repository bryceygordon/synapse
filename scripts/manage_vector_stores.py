import typer
from openai import OpenAI
from dotenv import load_dotenv

# Initialize Typer app and load environment variables
app = typer.Typer()
load_dotenv()
client = OpenAI()

@app.command()
def create(name: str):
    """
    Creates a new, empty vector store with the given name.
    """
    print(f"Creating vector store named '{name}'...")
    try:
        vector_store = client.vector_stores.create(name=name)
        print(f"✅ Success! Vector Store '{name}' created.")
        print(f"   ID: {vector_store.id}")
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")

@app.command()
def list():
    """
    Lists all available vector stores in your OpenAI organization.
    """
    print("Fetching vector stores...")
    try:
        vector_stores = client.vector_stores.list()
        if not vector_stores.data:
            print("No vector stores found.")
            return

        print("--- Available Vector Stores ---")
        for store in vector_stores.data:
            print(f"- Name: {store.name}, ID: {store.id}")
        print("-----------------------------")
    except Exception as e:
        print(f"❌ Error listing vector stores: {e}")

@app.command()
def delete(vector_store_id: str):
    """
    Deletes a vector store by its ID.
    """
    print(f"Attempting to delete vector store with ID: {vector_store_id}...")
    try:
        response = client.vector_stores.delete(vector_store_id=vector_store_id)
        if response.deleted:
            print(f"✅ Success! Vector store {vector_store_id} deleted.")
        else:
            print(f"⚠️ Deletion failed. Response: {response}")
    except Exception as e:
        print(f"❌ Error deleting vector store: {e}")

if __name__ == "__main__":
    app()
