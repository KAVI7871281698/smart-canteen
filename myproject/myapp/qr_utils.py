import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings
import os

def generate_qr_code(user):
    """
    Generates a QR code for the given user and saves it to the media directory.
    
    Args:
        user: User model instance for whom the QR code is being generated
        
    Returns:
        str: Path to the generated QR code image file
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Data to be encoded in QR code
    qr_data = f"user_id:{user.id},username:{user.username}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Prepare to save the image
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # Define file path
    filename = f'qr_{user.username}_{user.id}.png'
    filepath = os.path.join(settings.MEDIA_ROOT, 'qr_codes', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save the image
    with open(filepath, 'wb') as f:
        img.save(f)
    
    return filepath

def generate_qr_code_in_memory(user):
    """
    Generates a QR code for the given user and returns it as a BytesIO object.
    Useful for immediate display without saving to disk.
    
    Args:
        user: User model instance for whom the QR code is being generated
        
    Returns:
        BytesIO: In-memory file object containing the QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Data to be encoded in QR code
    qr_data = f"user_id:{user.id},username:{user.username}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to in-memory file
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer

def parse_qr_data(qr_data):
    """
    Parses the data from a scanned QR code into a dictionary.
    
    Args:
        qr_data (str): Raw data from QR code scanner
        
    Returns:
        dict: Parsed user data with keys 'user_id' and 'username'
        None: If QR data is invalid
    """
    try:
        parts = qr_data.split(',')
        user_id = parts[0].split(':')[1]
        username = parts[1].split(':')[1]
        return {
            'user_id': user_id,
            'username': username
        }
    except (IndexError, AttributeError):
        return None