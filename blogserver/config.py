"""Configuration file"""
class Config:
    """You can save these as environment variables in your OS!
        Also important to add this file to gitignore
    """
    SECRET_KEY = '4353b839bf36706685f4aafd88ec5158'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'anirudhsriram01@gmail.com'
    MAIL_PASSWORD = 'ivtcmyfncyyblgtn'
    AWS_ACCESS_KEY_ID = 'AKIA3X6M3C4ZIYSYM34B' 
    AWS_SECRET_KEY='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'


