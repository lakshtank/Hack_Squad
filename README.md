- Team Name : HackSquad
- Problem Statement : Skill Swap Platform
- Team Leader : Tank laksh
- Email : tanklaksh.2007@gmail.com
- Member 2 : Kunj vaghani
- Email : vaghanikunj2448@gmail.com
- Member 3 : Megh Patel
- Email : megh2850@gmail.com
- Member 4 : Nishtha Shah
- Email : nishthashah0106@gmail.com
# SkillSwap

A modern full-stack web application built with Flask, HTML, CSS, and JavaScript. SkillSwap is a platform designed to connect learners and teachers, enabling skill sharing and collaborative learning.

## Features

- **Modern Design**: Clean, responsive design with beautiful gradients and animations
- **User Authentication**: Complete signup and login system with session management
- **Password Reset**: Secure forgot password functionality with email verification
- **User Dashboard**: Personalized dashboard for authenticated users
- **Database Integration**: SQLite database with user management
- **File Upload**: Profile photo upload functionality
- **Multiple Pages**: Homepage, About, Contact, Signup, Login, and Dashboard
- **Interactive Elements**: Smooth scrolling, form validation, and hover effects
- **Mobile Responsive**: Optimized for all device sizes
- **Contact Form**: Functional contact form with client-side validation

## Project Structure

```
SkillSwap/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html        # Homepage
│   ├── about.html        # About page
│   └── contact.html      # Contact page
└── static/              # Static assets
    ├── css/
    │   └── style.css     # Main stylesheet
    └── js/
        └── main.js       # JavaScript functionality
```

## Installation

1. **Clone or download the project**
   ```bash
   cd SkillSwap
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure email settings (for password reset functionality)**
   
   Edit `app.py` and update the email configuration:
   ```python
   app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Your Gmail address
   app.config['MAIL_PASSWORD'] = 'your-app-password'     # Your Gmail app password
   app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
   ```
   
   **Note**: For Gmail, you'll need to:
   - Enable 2-factor authentication
   - Generate an app password
   - Use the app password instead of your regular password

## Running the Application

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to**
   ```
   http://localhost:8000
   ```

## Pages

- **Homepage** (`/`): Landing page with hero section, features, and call-to-action
- **About** (`/about`): Information about SkillSwap's mission, vision, and team
- **Contact** (`/contact`): Contact form and company information
- **Signup** (`/signup`): User registration with profile photo upload
- **Login** (`/login`): User authentication with forgot password link
- **Forgot Password** (`/forgot-password`): Password reset request form
- **Reset Password** (`/reset-password/<token>`): Password reset form with token validation
- **Dashboard** (`/dashboard`): Personalized user dashboard (requires authentication)

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with modern design principles
- **Fonts**: Inter (Google Fonts)
- **Icons**: Emoji icons for simplicity

## Features Implemented

### Frontend
- Responsive design with mobile-first approach
- Modern gradient backgrounds and smooth animations
- Interactive hover effects and transitions
- Form validation with user feedback
- Smooth scrolling navigation

### Backend
- Flask routing for multiple pages
- User authentication with Flask-Login
- Password reset functionality with email verification
- SQLite database with SQLAlchemy ORM
- Password hashing with Werkzeug
- File upload handling
- Session management
- Template rendering with Jinja2
- Static file serving
- Development server configuration

### JavaScript Functionality
- Smooth scrolling for anchor links
- Contact form validation and submission
- Dynamic navbar effects on scroll
- Interactive card hover effects
- Button ripple animations
- Console welcome messages

## Customization

### Styling
- Modify `static/css/style.css` to change colors, fonts, and layout
- The color scheme uses blue tones (`#2563eb`) as the primary color
- Gradients and shadows can be adjusted in the CSS file

### Content
- Edit HTML templates in the `templates/` directory
- Update text content, images, and links as needed
- Modify the navigation menu in each template

### Functionality
- Add new routes in `app.py` for additional pages
- Extend JavaScript functionality in `static/js/main.js`
- Implement backend form processing for the contact form

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Development

To extend the application:

1. **Add new pages**: Create new routes in `app.py` and corresponding HTML templates
2. **Enhance styling**: Modify the CSS file for custom designs
3. **Add functionality**: Extend the JavaScript file with new interactive features
4. **Database integration**: Add Flask-SQLAlchemy for data persistence
5. **User authentication**: Implement Flask-Login for user management

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**SkillSwap** - Connect, Learn, Grow 🎓 
>>>>>>> 2029dfa (initial commit)
>>>>>>> b2f455a (Intial)
