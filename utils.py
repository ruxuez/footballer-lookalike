from facenet_pytorch import InceptionResnetV1
from facenet_pytorch import MTCNN
from PIL import Image
import torch
from sqlalchemy import create_engine
import pandas as pd
from io import BytesIO
import requests
import streamlit as st


# Database connection parameters from .streamlit/secrets.toml
db_config = {
    "username": st.secrets["database"]["user"],
    "password": st.secrets["database"]["password"],
    "host": st.secrets["database"]["host"],
    "port": st.secrets["database"]["port"],
    "dbname": st.secrets["database"]["dbname"],
}

# Create the connection URL from the dictionary
connection_url = (
    f"postgresql://"
    f"{db_config['username']}:{db_config['password']}@"
    f"{db_config['host']}:{db_config['port']}/"
    f"{db_config['dbname']}"
)

# Create the engine
engine = create_engine(connection_url)


class FacenetEmbedder:
    def __init__(self):
        # Set the device to use GPU if available; otherwise, use CPU
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # Initialize MTCNN (Multi-Task Cascaded Convolutional Networks) for face detection
        self.mtcnn = MTCNN(device=self.device)
        # Initialize InceptionResnetV1 model pretrained on VGGFace2 dataset for face embedding
        self.resnet = InceptionResnetV1(
            pretrained="vggface2", device=self.device
        ).eval()

    # Method to detect face locations in a batch of images
    def detect_face(self, batch):
        # Return face coordinates detected by MTCNN
        faces = self.mtcnn.detect(batch)
        return faces

    # Method to encode a batch of face images into embeddings
    def encode(self, batch):
        # Preprocess and detect faces in the batch
        face_batch = self.mtcnn(batch)
        # Filter out None values (images without detected faces)
        face_batch = [i for i in face_batch if i is not None]
        # Stack the valid face tensors into a single tensor
        aligned = torch.stack(face_batch)
        # Move the tensor to GPU if using GPU
        if self.device.type == "cuda":
            aligned = aligned.to(self.device)
        # Generate face embeddings using the ResNet model and return as a list
        embeddings = self.resnet(aligned).detach().cpu()
        return embeddings.tolist()


# Function to preprocess and reshape a batch of images
def reshape(batch):
    batch = [image.convert("RGB").resize((421, 632)) for image in batch]
    return batch


# Function to find similar faces in the database
def find_similar_faces(facenet, face, country="Any", competition="Any", gender="Any"):
    # Encode the given face into a 512-dimensional embedding
    emb = facenet.encode([face.convert("RGB")])[0]
    # Build the WHERE clause dynamically based on conditions
    country_clause = "" if country == "Any" else f"'{country}' = ANY(nationality)"
    competition_clause = "" if competition == "Any" else f"c.name = '{competition}'"
    gender_clause = "" if gender == "Any" else f"c.gender = '{gender}'"

    # Combine the clauses using logical AND if both are present
    where_clause = " AND ".join(
        filter(None, [country_clause, competition_clause, gender_clause])
    )
    where_clause = f"WHERE {where_clause}" if where_clause else ""

    # <=>: cosine distance, sqrt(512): mximum possible vector distance for 512 dimentional, *2: vectors range from -1 to 1
    query = """SELECT p.name, p.nationality, p.gender, city_of_birth, country_of_birth, date_of_birth, position, 
                club_name, joined_on, height, market_value,
                array_agg(c.name) AS competitions_names,
                image_url, 1-(image_embedding <=> '{emb}')/(sqrt(512)*2) as similarity
                FROM all_players_embeddings p
                JOIN competitions c
                ON c.id = ANY(p.competitions)
                {where_clause}
                GROUP BY p.name, p.player_id, p.nationality, p.gender, city_of_birth, country_of_birth, date_of_birth, position, 
                club_name, joined_on, height, market_value, image_url, similarity
                ORDER BY similarity desc LIMIT 1;""".format(
        emb=emb, where_clause=where_clause
    )
    print(query)
    # Execute the query and fetch results into a pandas DataFrame
    r = pd.read_sql_query(query, con=engine)
    # Download images for the results and add them to the DataFrame
    r["image"] = r["image_url"].apply(
        lambda x: Image.open(BytesIO(requests.get(f"""{x}""").content))
    )
    # Convert the DataFrame to a dictionary with records orientation
    r = r.to_dict(orient="records")
    return r


# Initialize the FacenetEmbedder instance
facenet = FacenetEmbedder()

# Example: Generate embeddings for a face image (commented for placeholder purposes)
# embeddings = facenet.encode(face_image)
