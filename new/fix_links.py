import os
import re

folder = "templates"

# All link replacements
replacements = {
    'href="index.html"': 'href="/"',
    "href='index.html'": "href='/'",
    'href="login.html"': 'href="/login"',
    "href='login.html'": "href='/login'",
    'href="signup.html"': 'href="/signup"',
    "href='signup.html'": "href='/signup'",
    'href="studenthome.html"': 'href="/studenthome"',
    "href='studenthome.html'": "href='/studenthome'",
    'href="teacherhome.html"': 'href="/teacherhome"',
    "href='teacherhome.html'": "href='/teacherhome'",
    'href="parenthome.html"': 'href="/parenthome"',
    "href='parenthome.html'": "href='/parenthome'",
    'href="adminhome.html"': 'href="/adminhome"',
    "href='adminhome.html'": "href='/adminhome'",
    'href="profile.html"': 'href="/profile"',
    "href='profile.html'": "href='/profile'",
    'href="messages.html"': 'href="/messages"',
    "href='messages.html'": "href='/messages'",
    'href="attendance.html"': 'href="/attendance"',
    "href='attendance.html'": "href='/attendance'",
    'href="results.html"': 'href="/results"',
    "href='results.html'": "href='/results'",
    'href="assignment.html"': 'href="/assignment"',
    "href='assignment.html'": "href='/assignment'",
    'href="gallery.html"': 'href="/gallery"',
    "href='gallery.html'": "href='/gallery'",
    'href="contact.html"': 'href="/contact"',
    "href='contact.html'": "href='/contact'",
    'href="about us.html"': 'href="/about"',
    "href='about us.html'": "href='/about'",
    'href="liberary.html"': 'href="/liberary"',
    "href='liberary.html'": "href='/liberary'",
    'href="news.html"': 'href="/news"',
    "href='news.html'": "href='/news'",
    'href="teachers.html"': 'href="/teachers"',
    "href='teachers.html'": "href='/teachers'",
    'href="students.html.html"': 'href="/students"',
    "href='students.html.html'": "href='/students'",
    'href="post-news.html"': 'href="/post-news"',
    "href='post-news.html'": "href='/post-news'",
    'href="post-assignment.html"': 'href="/post-assignment"',
    "href='post-assignment.html'": "href='/post-assignment'",
    'href="post-result.html"': 'href="/post-result"',
    "href='post-result.html'": "href='/post-result'",
    'href="post-attendance.html"': 'href="/post-attendance"',
    "href='post-attendance.html'": "href='/post-attendance'",
    'href="manage-students.html"': 'href="/manage-students"',
    "href='manage-students.html'": "href='/manage-students'",
    'href="manage-teachers.html"': 'href="/manage-teachers"',
    "href='manage-teachers.html'": "href='/manage-teachers'",
    'href="manage-parents.html"': 'href="/manage-parents"',
    "href='manage-parents.html'": "href='/manage-parents'",
    'href="admin-report.html"': 'href="/admin-report"',
    "href='admin-report.html'": "href='/admin-report'",
    'href="logout.html"': 'href="/logout"',
    "href='logout.html'": "href='/logout'",
    'window.location.href = "index.html"': 'window.location.href = "/"',
    "window.location.href = 'index.html'": "window.location.href = '/'",
    'window.location.href = "login.html"': 'window.location.href = "/login"',
    "window.location.href = 'login.html'": "window.location.href = '/login'",
    'window.location.href = "signup.html"': 'window.location.href = "/signup"',
    "window.location.href = 'signup.html'": "window.location.href = '/signup'",
    'window.location.href = "studenthome.html"': 'window.location.href = "/studenthome"',
    "window.location.href = 'studenthome.html'": "window.location.href = '/studenthome'",
    'window.location.href = "teacherhome.html"': 'window.location.href = "/teacherhome"',
    "window.location.href = 'teacherhome.html'": "window.location.href = '/teacherhome'",
    'window.location.href = "parenthome.html"': 'window.location.href = "/parenthome"',
    "window.location.href = 'parenthome.html'": "window.location.href = '/parenthome'",
    'window.location.href = "adminhome.html"': 'window.location.href = "/adminhome"',
    "window.location.href = 'adminhome.html'": "window.location.href = '/adminhome'",
}

def fix_all_files():
    html_files = [f for f in os.listdir(folder) if f.endswith('.html')]
    
    fixed_count = 0
    for filename in html_files:
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply all replacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Also fix any href="something.html" that might have been missed
        # This catches any remaining .html links
        content = re.sub(r'href="([^"]+)\.html"', r'href="/\1"', content)
        content = re.sub(r"href='([^']+)\.html'", r"href='/\1'", content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filename}")
            fixed_count += 1
        else:
            print(f"⏭️ No changes: {filename}")
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == "__main__":
    print("🔧 Fixing all HTML links...")
    fix_all_files()
    print("\n✅ All done! Run 'python app.py'")