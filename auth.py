import json
import os
import socket
from cryptography.fernet import Fernet
import database
import biometric_utils

KEY_FILE = "secret.key"

def load_or_generate_key():
    """Loads the symmetric encryption key, or generates one if it doesn't exist."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

def get_fernet():
    key = load_or_generate_key()
    return Fernet(key)

def register_user(username):
    """
    Handles the registration flow:
    1. Captures face
    2. Generates embedding
    3. Encrypts embedding
    4. Saves to database
    """
    if database.get_user(username):
        print("Error: User already exists. Please choose a different username.")
        return False
        
    print(f"Registering face for user: {username}")
    img_frame = biometric_utils.capture_face(window_name=f"Registration: {username}")
    
    if img_frame is None:
        print("Registration cancelled.")
        return False
        
    print("Processing face... Please wait.")
    embedding = biometric_utils.get_face_embedding(img_frame)
    if embedding is None:
        print("Error: Could not detect a face clearly. Registration failed.")
        return False
        
    # Serialize embedding vector to JSON string, then encrypt
    embedding_json = json.dumps(embedding)
    fernet = get_fernet()
    encrypted_embedding = fernet.encrypt(embedding_json.encode('utf-8'))
    
    success = database.add_user(username, encrypted_embedding)
    if success:
        print("Registration successful! Your biometric data is securely stored.")
        return True
    else:
        print("Database error during registration.")
        return False

def login_user(username):
    """
    Handles the login flow:
    1. Fetches encrypted embedding from database
    2. Decrypts to get original embedding vector
    3. Captures fresh face
    4. Compares distances
    """
    system_ip = socket.gethostbyname(socket.gethostname())
    
    encrypted_data = database.get_user(username)
    if not encrypted_data:
        print("Error: User not found. Please register first.")
        database.log_auth_attempt(username, "FAIL_INVALID_USER", None, system_ip)
        return False
        
    print(f"User {username} found. Waiting for facial scan...")
    
    fernet = get_fernet()
    try:
        decrypted_json = fernet.decrypt(encrypted_data).decode('utf-8')
        stored_embedding = json.loads(decrypted_json)
    except Exception as e:
        print(f"Error decrypting biometric profile: {e}")
        return False

    img_frame = biometric_utils.capture_face(window_name=f"Login: {username}")
    if img_frame is None:
        print("Login cancelled.")
        return False
        
    print("Analyzing face...")
    live_embedding = biometric_utils.get_face_embedding(img_frame)
    if live_embedding is None:
        print("Error: Could not detect face during login scan.")
        database.log_auth_attempt(username, "FAIL_NO_FACE", None, system_ip)
        return False
        
    match, distance = biometric_utils.verify_embedding_distance(live_embedding, stored_embedding)
    
    if match:
        print("\n===============================")
        print(f"   LOGIN SUCCESSFUL!           ")
        print(f"   Welcome back, {username}!   ")
        print("===============================\n")
        database.log_auth_attempt(username, "SUCCESS", distance, system_ip)
        return True
    else:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("   LOGIN FAILED!               ")
        print("   Identity verification failed")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        database.log_auth_attempt(username, "FAIL", distance, system_ip)
        return False
