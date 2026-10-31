import os
import time
import threading
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip

try:
    import pyautogui
except ImportError:
    pyautogui = None

app = Flask(__name__)
driver = None

def get_driver():
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        # Ensure your Chrome User Data directory path is correct
        user_data_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        options.add_argument(f"--user-data-dir={user_data_path}")
        options.add_argument(r"--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
    return driver

def bypass_common_popups(d):
    popup_xpaths = [
        "//div[contains(text(), 'Want to create an ad post?')]//ancestor::div[contains(@role, 'banner') or contains(@role, 'region') or contains(@class, 'x')]//button[contains(@aria-label, 'Close') or text()='Close']",
        "//button[contains(., 'Got it')]",
        "//div[@role='button' and contains(., 'Got it')]",
        "//button[contains(text(), 'Not Now')]",
        "//button[contains(text(), 'Dismiss')]",
        "//button[contains(text(), 'Cancel')]",
        "//button[contains(@aria-label, 'Close')]"
    ]
    for xpath in popup_xpaths:
        try:
            for el in d.find_elements(By.XPATH, xpath):
                if el.is_displayed():
                    d.execute_script("arguments[0].click();", el)
                    time.sleep(1)
        except Exception:
            pass

def run_tiktok(video_path, caption):
    d = get_driver()
    d.get("https://www.tiktok.com/tiktokstudio/upload")
    wait = WebDriverWait(d, 35)
    time.sleep(4)
    bypass_common_popups(d)
    
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    file_input.send_keys(os.path.abspath(video_path))
    
    if caption:
        try:
            cap_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".public-DraftEditor-content, div[contenteditable='true']")))
            cap_box.send_keys(caption)
        except Exception:
            pass
            
    time.sleep(10)
    bypass_common_popups(d)
    d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    for xpath in ["//button[normalize-space()='Post']", "//button[contains(@class, 'btn-post')]", "//button[contains(., 'Post')]"]:
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            d.execute_script("arguments[0].click();", d.find_element(By.XPATH, xpath))
            break
        except Exception:
            continue
            
    time.sleep(2)
    for xp in ["//button[normalize-space()='Post now']", "//button[contains(., 'Post now')]"]:
        try:
            p_btn = WebDriverWait(d, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            d.execute_script("arguments[0].click();", p_btn)
            break
        except Exception:
            pass

def run_meta(video_path, caption):
    d = get_driver()
    d.get("https://business.facebook.com/latest/composer")
    wait = WebDriverWait(d, 35)
    time.sleep(5)
    bypass_common_popups(d)
    
    pyperclip.copy(os.path.abspath(video_path))
    time.sleep(1)
    
    uploaded = False
    for inp in d.find_elements(By.CSS_SELECTOR, "input[type='file']"):
        try:
            d.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", inp)
            inp.send_keys(os.path.abspath(video_path))
            uploaded = True
            break
        except Exception:
            continue
            
    if not uploaded:
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][contains(., 'Add photo/video')] | //button[contains(., 'Add photo/video')]")))
            d.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
            time.sleep(1)
            add_btn.click()
            time.sleep(2)
            if pyautogui:
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
        except Exception:
            pass
            
    time.sleep(3)
    if caption:
        try:
            txt_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox'], div[contenteditable='true']")))
            txt_box.click()
            txt_box.send_keys(caption)
        except Exception:
            pass
            
    for _ in range(60):
        if not any(el.is_displayed() for el in d.find_elements(By.XPATH, "//*[contains(text(), 'Processing media')]")):
            break
        time.sleep(2)
        
    for _ in range(25):
        bypass_common_popups(d)
        try:
            pub_btn = d.find_element(By.XPATH, "//div[@aria-label='Publish' or @aria-label='Post' or contains(text(), 'Publish')][not(@aria-disabled='true') and not(contains(@class, 'disabled'))]")
            if pub_btn.is_displayed():
                d.execute_script("arguments[0].click();", pub_btn)
                break
        except Exception:
            pass
        time.sleep(2)

def run_youtube(video_path, caption):
    d = get_driver()
    d.get("https://studio.youtube.com")
    wait = WebDriverWait(d, 35)
    time.sleep(4)
    bypass_common_popups(d)
    
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "create-icon"))).click()
        time.sleep(1.5)
        wait.until(EC.element_to_be_clickable((By.ID, "text-item-0"))).click()
    except Exception:
        pass
        
    time.sleep(2)
    try:
        inp = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        inp.send_keys(os.path.abspath(video_path))
    except Exception:
        pass
        
    time.sleep(6)
    if caption:
        try:
            boxes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#textbox")))
            if len(boxes) > 1:
                boxes[1].send_keys(caption)
        except Exception:
            pass
            
    try:
        not_kids = wait.until(EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']")))
        not_kids.click()
    except Exception:
        pass
        
    for _ in range(3):
        time.sleep(2)
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "next-button"))).click()
        except Exception:
            break
            
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']"))).click()
    except Exception:
        pass
        
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button'] | //div[contains(text(), 'Publish')]/ancestor::ytcp-button"))).click()
    except Exception:
        pass

def run_instagram(video_path, caption):
    d = get_driver()
    d.get("https://www.instagram.com")
    wait = WebDriverWait(d, 30)
    bypass_common_popups(d)
    
    try:
        svg = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='New post'], svg[aria-label='Nayi post']")))
        svg.find_element(By.XPATH, "./ancestor::a | ./ancestor::div[contains(@role, 'button')]").click()
        time.sleep(3)
        
        inp = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        inp.send_keys(os.path.abspath(video_path))
        time.sleep(8)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Aage')]"))).click()
        time.sleep(3)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Aage')]"))).click()
        time.sleep(3)
        
        if caption:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Write a caption...'], div[contenteditable='true']"))).send_keys(caption)
            time.sleep(2)
            
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Share' or text()='Sajha karein')]"))).click()
    except Exception as e:
        print(f"Instagram error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/publish', methods=['POST'])
def trigger_publish():
    data = request.json or {}
    platform = data.get('platform')
    video_path = data.get('video_path')
    caption = data.get('caption', '')

    if not video_path or not os.path.exists(video_path):
        return jsonify({"status": "error", "message": "Video file ka path galat hai ya file maujood nahi hai!"})

    targets = {
        "tiktok": run_tiktok,
        "meta": run_meta,
        "youtube": run_youtube,
        "instagram": run_instagram
    }

    func = targets.get(platform)
    if not func:
        return jsonify({"status": "error", "message": "Invalid platform!"})

    threading.Thread(target=func, args=(video_path, caption), daemon=True).start()
    return jsonify({"status": "success", "message": f"{platform.upper()} automated publish sequence trigger ho gaya!"})

if __name__ == '__main__':
    print("Serving on http://localhost:5000")
    app.run(port=5000, debug=False)