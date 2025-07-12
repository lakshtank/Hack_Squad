import os
import uuid
import random
import string
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Change this to your email
app.config['MAIL_PASSWORD'] = 'your-app-password'     # Change this to your app password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

# For development/testing - set to True to show reset links instead of sending emails
app.config['SHOW_RESET_LINKS'] = True

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to profile
    profile = db.relationship('Profile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Profile model
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic Information
    current_profession = db.Column(db.String(100))
    current_organization = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    
    # Skills
    skills_offering = db.Column(db.Text)  # JSON string of skills
    skills_wanting = db.Column(db.Text)   # JSON string of skills
    
    # Experience
    experience_years = db.Column(db.Integer)  # Years of experience
    experience_details = db.Column(db.Text)   # Detailed experience description
    
    # Education & Certificates
    education = db.Column(db.Text)  # JSON string of education entries
    certificates = db.Column(db.Text)  # JSON string of certificates
    
    # Availability & Settings
    availability = db.Column(db.String(50))  # weekdays, weekends, evenings
    is_public = db.Column(db.Boolean, default=True)
    bio = db.Column(db.Text)
    
    # Timestamps
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Swap Request model
class SwapRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_requests')

# Swap Feedback model
class SwapFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swap_id = db.Column(db.Integer, db.ForeignKey('swap_request.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    swap = db.relationship('SwapRequest', backref='feedbacks')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='given_feedbacks')
    reviewed = db.relationship('User', foreign_keys=[reviewed_id], backref='received_feedbacks')

# Password Reset model
class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    secret_code = db.Column(db.String(6), nullable=False)  # 6-digit secret code
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref='password_resets')

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='chats_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='chats_as_user2')
    messages = db.relationship('ChatMessage', backref='chat', lazy='dynamic', order_by='ChatMessage.created_at')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')

def generate_secret_code():
    """Generate a 6-digit secret code."""
    return ''.join(random.choices(string.digits, k=6))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Context processor to add pending requests count to all templates
@app.context_processor
def inject_pending_requests():
    """Inject pending requests count into all templates"""
    if current_user.is_authenticated:
        # Update last_seen timestamp for active user
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
        pending_requests_count = SwapRequest.query.filter_by(
            receiver_id=current_user.id,
            status='pending'
        ).count()
        return {'pending_requests_count': pending_requests_count}
    return {'pending_requests_count': 0}

@app.context_processor
def inject_unread_messages():
    """Inject unread message count into all templates"""
    if current_user.is_authenticated:
        # Get all chats where current user is involved
        chats = Chat.query.filter(
            db.or_(
                Chat.user1_id == current_user.id,
                Chat.user2_id == current_user.id
            )
        ).all()
        
        total_unread = 0
        for chat in chats:
            unread_count = chat.messages.filter(
                db.and_(
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read == False
                )
            ).count()
            total_unread += unread_count
        
        return {'unread_messages_count': total_unread}
    return {'unread_messages_count': 0}

# Routes
@app.route('/')
def homepage():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location')
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('signup.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('signup.html')
        
        # Handle profile photo upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                profile_photo = f'uploads/{filename}'
        
        # Create new user
        user = User(
            full_name=full_name,
            email=email,
            location=location,
            profile_photo=profile_photo
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user automatically
        login_user(user)
        # Clear any existing flash messages
        session.pop('_flashes', None)
        flash('Account created successfully! Please complete your profile.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Update last_seen timestamp
            user.last_seen = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    # Clear any existing flash messages
    session.pop('_flashes', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('homepage'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot_password.html')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email.', 'error')
            return render_template('forgot_password.html')
        # Show reset password form directly
        return render_template('reset_password_direct.html', email=email)
    return render_template('forgot_password.html')

@app.route('/reset-password-direct', methods=['POST'])
def reset_password_direct():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if not email or not password or not confirm_password:
        flash('Please fill in all fields.', 'error')
        return render_template('reset_password_direct.html', email=email)
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return render_template('reset_password_direct.html', email=email)
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return render_template('reset_password_direct.html', email=email)
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('No account found with that email.', 'error')
        return render_template('reset_password_direct.html', email=email)
    user.set_password(password)
    db.session.commit()
    flash('Your password has been reset successfully. Please log in with your new password.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's profile and parse JSON skills data
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    # Parse JSON data for skills
    import json
    skills_offering = []
    skills_wanting = []
    education = []
    certificates = []
    
    if profile:
        try:
            skills_offering = json.loads(profile.skills_offering) if profile.skills_offering else []
            skills_wanting = json.loads(profile.skills_wanting) if profile.skills_wanting else []
            education = json.loads(profile.education) if profile.education else []
            certificates = json.loads(profile.certificates) if profile.certificates else []
        except:
            skills_offering = []
            skills_wanting = []
            education = []
            certificates = []
    
    return render_template('dashboard.html', skills_offering=skills_offering, skills_wanting=skills_wanting, education=education, certificates=certificates)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get form data
        current_profession = request.form.get('current_profession', '')
        current_organization = request.form.get('current_organization', '')
        location = request.form.get('location', '')
        website = request.form.get('website', '')
        linkedin = request.form.get('linkedin', '')
        github = request.form.get('github', '')
        
        skills_offering = request.form.getlist('skills_offering')
        skills_wanting = request.form.getlist('skills_wanting')
        
        experience_years = request.form.get('experience_years', type=int)
        experience_details = request.form.get('experience_details', '')
        
        education = request.form.getlist('education')
        certificates = request.form.getlist('certificates')
        
        availability = request.form.get('availability')
        is_public = request.form.get('is_public') == 'on'
        bio = request.form.get('bio', '')
        
        # Convert lists to JSON strings
        import json
        skills_offering_json = json.dumps(skills_offering)
        skills_wanting_json = json.dumps(skills_wanting)
        education_json = json.dumps(education)
        certificates_json = json.dumps(certificates)
        
        # Check if profile exists
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        
        if profile:
            # Update existing profile
            profile.current_profession = current_profession
            profile.current_organization = current_organization
            profile.location = location
            profile.website = website
            profile.linkedin = linkedin
            profile.github = github
            profile.skills_offering = skills_offering_json
            profile.skills_wanting = skills_wanting_json
            profile.experience_years = experience_years
            profile.experience_details = experience_details
            profile.education = education_json
            profile.certificates = certificates_json
            profile.availability = availability
            profile.is_public = is_public
            profile.bio = bio
        else:
            # Create new profile
            profile = Profile(
                user_id=current_user.id,
                current_profession=current_profession,
                current_organization=current_organization,
                location=location,
                website=website,
                linkedin=linkedin,
                github=github,
                skills_offering=skills_offering_json,
                skills_wanting=skills_wanting_json,
                experience_years=experience_years,
                experience_details=experience_details,
                education=education_json,
                certificates=certificates_json,
                availability=availability,
                is_public=is_public,
                bio=bio
            )
            db.session.add(profile)
        
        db.session.commit()
        # Clear any existing flash messages
        session.pop('_flashes', None)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get existing profile data
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    # Parse JSON data for form
    import json
    skills_offering = []
    skills_wanting = []
    education = []
    certificates = []
    
    if profile:
        try:
            skills_offering = json.loads(profile.skills_offering) if profile.skills_offering else []
            skills_wanting = json.loads(profile.skills_wanting) if profile.skills_wanting else []
            education = json.loads(profile.education) if profile.education else []
            certificates = json.loads(profile.certificates) if profile.certificates else []
        except:
            skills_offering = []
            skills_wanting = []
            education = []
            certificates = []
    
    return render_template('profile.html', profile=profile, skills_offering=skills_offering, skills_wanting=skills_wanting, education=education, certificates=certificates)

@app.route('/browse')
def browse():
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Get all public profiles with their users, excluding current user
    query = db.session.query(Profile, User).join(User).filter(Profile.is_public == True)
    
    # Exclude current user if logged in
    if current_user.is_authenticated:
        query = query.filter(User.id != current_user.id)
    
    # Apply search filter if query provided
    if search_query:
        import json
        # Search in skills_offering and skills_wanting
        query = query.filter(
            db.or_(
                Profile.skills_offering.contains(search_query),
                Profile.skills_wanting.contains(search_query)
            )
        )
    
    # Get results
    results = query.all()
    
    # Process results to parse JSON skills and get request status
    import json
    processed_results = []
    
    for profile, user in results:
        try:
            skills_offering = json.loads(profile.skills_offering) if profile.skills_offering else []
            skills_wanting = json.loads(profile.skills_wanting) if profile.skills_wanting else []
            education = json.loads(profile.education) if profile.education else []
            certificates = json.loads(profile.certificates) if profile.certificates else []
        except:
            skills_offering = []
            skills_wanting = []
            education = []
            certificates = []
        
        # Additional search filtering for exact skill matches
        if search_query:
            search_lower = search_query.lower()
            offering_matches = any(search_lower in skill.lower() for skill in skills_offering)
            wanting_matches = any(search_lower in skill.lower() for skill in skills_wanting)
            
            if not (offering_matches or wanting_matches):
                continue
        
        # Get request status if user is authenticated
        request_status = None
        if current_user.is_authenticated:
            # Check for existing request in either direction
            existing_request = SwapRequest.query.filter(
                db.or_(
                    db.and_(SwapRequest.sender_id == current_user.id, SwapRequest.receiver_id == user.id),
                    db.and_(SwapRequest.sender_id == user.id, SwapRequest.receiver_id == current_user.id)
                )
            ).first()
            
            if existing_request:
                if existing_request.sender_id == current_user.id:
                    request_status = existing_request.status  # sent by current user
                else:
                    request_status = existing_request.status  # received by current user
        
        processed_results.append({
            'user': user,
            'profile': profile,
            'skills_offering': skills_offering,
            'skills_wanting': skills_wanting,
            'education': education,
            'certificates': certificates,
            'request_status': request_status
        })
    
    return render_template('browse.html', results=processed_results, search_query=search_query)

@app.route('/view_profile/<int:user_id>')
def view_profile(user_id):
    """View a specific user's full profile"""
    user = User.query.get_or_404(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    if not profile or not profile.is_public:
        flash('Profile not found or is private.', 'error')
        return redirect(url_for('browse'))
    
    # Parse JSON data for skills, education, and certificates
    import json
    skills_offering = []
    skills_wanting = []
    education = []
    certificates = []
    
    try:
        skills_offering = json.loads(profile.skills_offering) if profile.skills_offering else []
        skills_wanting = json.loads(profile.skills_wanting) if profile.skills_wanting else []
        education = json.loads(profile.education) if profile.education else []
        certificates = json.loads(profile.certificates) if profile.certificates else []
    except:
        skills_offering = []
        skills_wanting = []
        education = []
        certificates = []
    
    # Get request status if user is authenticated
    request_status = None
    if current_user.is_authenticated and current_user.id != user_id:
        # Check for existing request in either direction
        existing_request = SwapRequest.query.filter(
            db.or_(
                db.and_(SwapRequest.sender_id == current_user.id, SwapRequest.receiver_id == user_id),
                db.and_(SwapRequest.sender_id == user_id, SwapRequest.receiver_id == current_user.id)
            )
        ).first()
        
        if existing_request:
            if existing_request.sender_id == current_user.id:
                request_status = existing_request.status  # sent by current user
            else:
                request_status = existing_request.status  # received by current user
    
    return render_template('view_profile.html', 
                         user=user, 
                         profile=profile, 
                         skills_offering=skills_offering, 
                         skills_wanting=skills_wanting,
                         education=education,
                         certificates=certificates,
                         request_status=request_status)

@app.route('/send_request', methods=['POST'])
@login_required
def send_request():
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('message', '')
    
    if not receiver_id:
        flash('Invalid request.', 'error')
        return redirect(url_for('browse'))
    
    # Check if user is trying to send request to themselves
    if int(receiver_id) == current_user.id:
        flash('You cannot send a request to yourself.', 'error')
        return redirect(url_for('browse'))
    
    # Check if request already exists (either direction)
    existing_request = SwapRequest.query.filter(
        db.or_(
            db.and_(SwapRequest.sender_id == current_user.id, SwapRequest.receiver_id == receiver_id),
            db.and_(SwapRequest.sender_id == receiver_id, SwapRequest.receiver_id == current_user.id)
        )
    ).first()
    
    if existing_request:
        flash('A request already exists between you and this user.', 'error')
        return redirect(url_for('browse'))
    
    # Create new swap request
    swap_request = SwapRequest(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message=message
    )
    
    db.session.add(swap_request)
    db.session.commit()
    
    flash('Swap request sent successfully!', 'success')
    return redirect(url_for('browse'))

@app.route('/requests')
@login_required
def requests():
    # Get sent and received requests
    sent_requests = SwapRequest.query.filter_by(sender_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    received_requests = SwapRequest.query.filter_by(receiver_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    
    return render_template('requests.html', sent_requests=sent_requests, received_requests=received_requests)

@app.route('/respond_request', methods=['POST'])
@login_required
def respond_request():
    request_id = request.form.get('request_id')
    action = request.form.get('action')  # accept or reject
    
    if not request_id or action not in ['accept', 'reject']:
        flash('Invalid request.', 'error')
        return redirect(url_for('requests'))
    
    swap_request = SwapRequest.query.get(request_id)
    
    if not swap_request or swap_request.receiver_id != current_user.id:
        flash('Request not found.', 'error')
        return redirect(url_for('requests'))
    
    if action == 'accept':
        # Accept the request
        swap_request.status = 'accepted'
        
        # Create a reciprocal accepted request for the other user
        reciprocal_request = SwapRequest(
            sender_id=swap_request.receiver_id,
            receiver_id=swap_request.sender_id,
            status='accepted',
            message=f"Reciprocal request for: {swap_request.message}"
        )
        
        db.session.add(reciprocal_request)
        flash('Swap request accepted! Both users can now see each other.', 'success')
    else:
        swap_request.status = 'rejected'
        flash('Swap request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('requests'))

@app.route('/cancel_request', methods=['POST'])
@login_required
def cancel_request():
    request_id = request.form.get('request_id')
    
    if not request_id:
        flash('Invalid request.', 'error')
        return redirect(url_for('requests'))
    
    swap_request = SwapRequest.query.get(request_id)
    
    if not swap_request or swap_request.sender_id != current_user.id:
        flash('Request not found.', 'error')
        return redirect(url_for('requests'))
    
    if swap_request.status != 'pending':
        flash('Cannot cancel non-pending request.', 'error')
        return redirect(url_for('requests'))
    
    db.session.delete(swap_request)
    db.session.commit()
    
    flash('Request cancelled successfully.', 'success')
    return redirect(url_for('requests'))

@app.route('/give_feedback', methods=['GET', 'POST'])
@login_required
def give_feedback():
    swap_id = request.args.get('swap_id') if request.method == 'GET' else request.form.get('swap_id')
    
    if not swap_id:
        flash('Invalid swap request.', 'error')
        return redirect(url_for('requests'))
    
    swap_request = SwapRequest.query.get(swap_id)
    
    if not swap_request or swap_request.status != 'accepted':
        flash('Swap request not found or not accepted.', 'error')
        return redirect(url_for('requests'))
    
    # Check if user is part of this swap
    if current_user.id not in [swap_request.sender_id, swap_request.receiver_id]:
        flash('You are not authorized to give feedback for this swap.', 'error')
        return redirect(url_for('requests'))
    
    # Determine who the user is reviewing
    if current_user.id == swap_request.sender_id:
        reviewed_user = swap_request.receiver
    else:
        reviewed_user = swap_request.sender
    
    # Check if user already gave feedback for this swap
    existing_feedback = SwapFeedback.query.filter_by(
        swap_id=swap_id,
        reviewer_id=current_user.id
    ).first()
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '')
        
        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            flash('Please provide a valid rating (1-5 stars).', 'error')
            return redirect(url_for('give_feedback', swap_id=swap_id))
        
        if existing_feedback:
            # Update existing feedback
            existing_feedback.rating = int(rating)
            existing_feedback.comment = comment
            flash('Feedback updated successfully!', 'success')
        else:
            # Create new feedback
            feedback = SwapFeedback(
                swap_id=swap_id,
                reviewer_id=current_user.id,
                reviewed_id=reviewed_user.id,
                rating=int(rating),
                comment=comment
            )
            db.session.add(feedback)
            flash('Feedback submitted successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('requests'))
    
    return render_template('give_feedback.html', 
                         swap_request=swap_request, 
                         reviewed_user=reviewed_user,
                         existing_feedback=existing_feedback)

@app.route('/view_feedback/<int:user_id>')
def view_feedback(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('browse'))
    
    # Get all feedback received by this user
    feedbacks = SwapFeedback.query.filter_by(reviewed_id=user_id).order_by(SwapFeedback.created_at.desc()).all()
    
    # Calculate average rating
    if feedbacks:
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        total_feedback = len(feedbacks)
    else:
        avg_rating = 0
        total_feedback = 0
    
    return render_template('view_feedback.html', 
                         user=user, 
                         feedbacks=feedbacks,
                         avg_rating=avg_rating,
                         total_feedback=total_feedback)

# Chat routes
@app.route('/chat')
@login_required
def chat():
    """Show list of all chats for the current user"""
    # Get all chats where current user is involved
    chats = Chat.query.filter(
        db.or_(
            Chat.user1_id == current_user.id,
            Chat.user2_id == current_user.id
        )
    ).order_by(Chat.updated_at.desc()).all()
    
    # Process chats to get the other user and last message
    chat_list = []
    for chat in chats:
        other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
        last_message = chat.messages.order_by(ChatMessage.created_at.desc()).first()
        unread_count = chat.messages.filter(
            db.and_(
                ChatMessage.sender_id != current_user.id,
                ChatMessage.is_read == False
            )
        ).count()
        
        chat_list.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    return render_template('chat_list.html', chats=chat_list)

@app.route('/chat/<int:chat_id>')
@login_required
def chat_room(chat_id):
    """Show specific chat room"""
    chat = Chat.query.get_or_404(chat_id)
    
    # Check if current user is part of this chat
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('chat'))
    
    # Get the other user
    other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
    
    # Mark messages as read
    unread_messages = chat.messages.filter(
        db.and_(
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        )
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    # Get messages
    messages = chat.messages.all()
    
    # Calculate online status
    now = datetime.utcnow()
    time_diff = now - other_user.last_seen
    
    if time_diff.total_seconds() < 300:  # 5 minutes
        online_status = "Online"
    else:
        minutes_ago = int(time_diff.total_seconds() / 60)
        if minutes_ago < 60:
            online_status = f"Last seen {minutes_ago} minutes ago"
        else:
            hours_ago = int(minutes_ago / 60)
            if hours_ago < 24:
                online_status = f"Last seen {hours_ago} hours ago"
            else:
                days_ago = int(hours_ago / 24)
                online_status = f"Last seen {days_ago} days ago"
    
    return render_template('chat_room.html', 
                         chat=chat, 
                         other_user=other_user, 
                         messages=messages,
                         online_status=online_status)

@app.route('/chat/start/<int:user_id>')
@login_required
def start_chat(user_id):
    """Start a new chat with a user"""
    if user_id == current_user.id:
        flash('You cannot start a chat with yourself.', 'error')
        return redirect(url_for('browse'))
    
    other_user = User.query.get_or_404(user_id)
    
    # Check if chat already exists
    existing_chat = Chat.query.filter(
        db.or_(
            db.and_(Chat.user1_id == current_user.id, Chat.user2_id == user_id),
            db.and_(Chat.user1_id == user_id, Chat.user2_id == current_user.id)
        )
    ).first()
    
    if existing_chat:
        return redirect(url_for('chat_room', chat_id=existing_chat.id))
    
    # Create new chat
    new_chat = Chat(user1_id=current_user.id, user2_id=user_id)
    db.session.add(new_chat)
    db.session.commit()
    
    return redirect(url_for('chat_room', chat_id=new_chat.id))

@app.route('/chat/send_message', methods=['POST'])
@login_required
def send_message():
    """Send a message in a chat"""
    try:
        chat_id = request.form.get('chat_id')
        message_text = request.form.get('message', '').strip()
        
        if not chat_id or not message_text:
            return jsonify({'success': False, 'error': 'Invalid message'})
        
        chat = Chat.query.get_or_404(chat_id)
        
        # Check if current user is part of this chat
        if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Create new message
        new_message = ChatMessage(
            chat_id=chat_id,
            sender_id=current_user.id,
            message=message_text
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': {
                'id': new_message.id,
                'message': new_message.message,
                'sender_id': new_message.sender_id,
                'created_at': new_message.created_at.strftime('%H:%M'),
                'sender_name': current_user.full_name
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat/get_messages/<int:chat_id>')
@login_required
def get_messages(chat_id):
    """Get messages for a chat (for AJAX updates)"""
    try:
        chat = Chat.query.get_or_404(chat_id)
        
        # Check if current user is part of this chat
        if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Mark messages as read
        unread_messages = chat.messages.filter(
            db.and_(
                ChatMessage.sender_id != current_user.id,
                ChatMessage.is_read == False
            )
        ).all()
        
        for message in unread_messages:
            message.is_read = True
        
        db.session.commit()
        
        # Get all messages
        messages = chat.messages.all()
        
        return jsonify({
            'success': True,
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'sender_id': msg.sender_id,
                'created_at': msg.created_at.strftime('%H:%M'),
                'sender_name': msg.sender.full_name,
                'is_mine': msg.sender_id == current_user.id
            } for msg in messages]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat/unread_count')
@login_required
def get_unread_count():
    """Get total unread message count for current user"""
    try:
        # Get all chats where current user is involved
        chats = Chat.query.filter(
            db.or_(
                Chat.user1_id == current_user.id,
                Chat.user2_id == current_user.id
            )
        ).all()
        
        total_unread = 0
        for chat in chats:
            unread_count = chat.messages.filter(
                db.and_(
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read == False
                )
            ).count()
            total_unread += unread_count
        
        return jsonify({
            'success': True,
            'unread_count': total_unread
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat/notifications')
@login_required
def get_chat_notifications():
    """Get recent unread messages for notifications"""
    try:
        # Get all chats where current user is involved
        chats = Chat.query.filter(
            db.or_(
                Chat.user1_id == current_user.id,
                Chat.user2_id == current_user.id
            )
        ).all()
        
        notifications = []
        for chat in chats:
            other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
            unread_messages = chat.messages.filter(
                db.and_(
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read == False
                )
            ).order_by(ChatMessage.created_at.desc()).limit(3).all()
            
            if unread_messages:
                notifications.append({
                    'chat_id': chat.id,
                    'other_user_name': other_user.full_name,
                    'unread_count': len(unread_messages),
                    'latest_message': unread_messages[0].message[:50] + '...' if len(unread_messages[0].message) > 50 else unread_messages[0].message
                })
        
        return jsonify({
            'success': True,
            'notifications': notifications
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Admin routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded admin credentials
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_users = User.query.count()
    total_swaps = SwapRequest.query.count()
    total_feedback = SwapFeedback.query.count()
    pending_swaps = SwapRequest.query.filter_by(status='pending').count()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_swaps=total_swaps,
                         total_feedback=total_feedback,
                         pending_swaps=pending_swaps)

@app.route('/admin/users')
def admin_users():
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    user = User.query.get(user_id)
    if user:
        # Delete related data
        SwapRequest.query.filter_by(sender_id=user_id).delete()
        SwapRequest.query.filter_by(receiver_id=user_id).delete()
        SwapFeedback.query.filter_by(reviewer_id=user_id).delete()
        SwapFeedback.query.filter_by(reviewed_id=user_id).delete()
        Profile.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.full_name} deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/swaps')
def admin_swaps():
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    swaps = SwapRequest.query.order_by(SwapRequest.created_at.desc()).all()
    return render_template('admin_swaps.html', swaps=swaps)

@app.route('/admin/delete_swap/<int:swap_id>', methods=['POST'])
def admin_delete_swap(swap_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    swap = SwapRequest.query.get(swap_id)
    if swap:
        # Delete related feedback
        SwapFeedback.query.filter_by(swap_id=swap_id).delete()
        
        db.session.delete(swap)
        db.session.commit()
        flash('Swap deleted successfully.', 'success')
    else:
        flash('Swap not found.', 'error')
    
    return redirect(url_for('admin_swaps'))

@app.route('/admin/feedback')
def admin_feedback():
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    feedbacks = SwapFeedback.query.order_by(SwapFeedback.created_at.desc()).all()
    return render_template('admin_feedback.html', feedbacks=feedbacks)

@app.route('/admin/delete_feedback/<int:feedback_id>', methods=['POST'])
def admin_delete_feedback(feedback_id):
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    feedback = SwapFeedback.query.get(feedback_id)
    if feedback:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted successfully.', 'success')
    else:
        flash('Feedback not found.', 'error')
    
    return redirect(url_for('admin_feedback'))

@app.route('/admin/download_csv/<report_type>')
def admin_download_csv(report_type):
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    from io import StringIO
    import csv
    
    si = StringIO()
    cw = csv.writer(si)
    
    if report_type == 'users':
        cw.writerow(['ID', 'Full Name', 'Email', 'Location', 'Created At'])
        users = User.query.all()
        for user in users:
            cw.writerow([user.id, user.full_name, user.email, user.location or '', user.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        filename = 'users_report.csv'
        
    elif report_type == 'swaps':
        cw.writerow(['ID', 'Sender', 'Receiver', 'Status', 'Message', 'Created At'])
        swaps = SwapRequest.query.all()
        for swap in swaps:
            cw.writerow([swap.id, swap.sender.full_name, swap.receiver.full_name, swap.status, swap.message or '', swap.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        filename = 'swaps_report.csv'
        
    elif report_type == 'feedback':
        cw.writerow(['ID', 'Swap ID', 'Reviewer', 'Reviewed', 'Rating', 'Comment', 'Created At'])
        feedbacks = SwapFeedback.query.all()
        for feedback in feedbacks:
            cw.writerow([feedback.id, feedback.swap_id, feedback.reviewer.full_name, feedback.reviewed.full_name, feedback.rating, feedback.comment or '', feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        filename = 'feedback_report.csv'
    
    else:
        flash('Invalid report type.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    output = si.getvalue()
    si.close()
    
    from flask import Response
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})

@app.route('/admin/message', methods=['GET', 'POST'])
def admin_message():
    if not session.get('admin_logged_in'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        message = request.form.get('message')
        message_type = request.form.get('message_type', 'info')
        
        if message:
            # Store the message in session for display
            session['platform_message'] = {
                'text': message,
                'type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            flash('Platform message sent successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Message cannot be empty.', 'error')
    
    return render_template('admin_message.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('platform_message', None)
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 