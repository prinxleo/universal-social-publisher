import os
import re
import time
import threading
from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
        "//div[contains(text(), \"Can't Read Files\")]//ancestor::div[@role='dialog']//div[@aria-label='Close' or text()='Close']",
        "//button[contains(., 'Got it')]",
        "//div[@role='button' and contains(., 'Got it')]",
        "//button[contains(text(), 'Not Now')]",
        "//button[contains(text(), 'Dismiss')]",
        "//button[contains(text(), 'Close')]",
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

# -------------------------------------------------------------
# 1. DIRECT FACEBOOK REEL / VIDEO AUTOMATION (CLICK BEFORE PASTE)
# -------------------------------------------------------------
def run_facebook_page(video_path, caption):
    try:
        d = get_driver()
        actions = ActionChains(d)
        abs_path = os.path.abspath(video_path)
        print("\n[FB] Step 1: Opening Facebook Page...")
        d.get("https://www.facebook.com/Itz.Biya.Official/")
        wait = WebDriverWait(d, 35)
        time.sleep(5)
        bypass_common_popups(d)

        # Trigger Reel / Photo-Video modal
        print("[FB] Step 2: Clicking Composer...")
        triggers = [
            "//span[text()='Reel']/ancestor::div[@role='button']",
            "//span[text()='Photo/video']/ancestor::div[@role='button']",
            "//div[@role='button'][.//span[contains(text(), 'Reel')]]",
            "//div[@role='button'][.//span[contains(text(), 'Photo/video')]]"
        ]
        for xpath in triggers:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                d.execute_script("arguments[0].click();", btn)
                print("[FB] Composer trigger clicked.")
                break
            except Exception:
                continue

        time.sleep(3)

        # Attach video strictly into video file input
        file_attached = False
        inputs = d.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for inp in inputs:
            try:
                accept = inp.get_attribute("accept") or ""
                if "video" in accept or accept == "":
                    d.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", inp)
                    inp.send_keys(abs_path)
                    file_attached = True
                    print("[FB] Success: Video file attached.")
                    break
            except Exception:
                continue

        if not file_attached and pyautogui:
            pyperclip.copy(abs_path)
            try:
                dropzone = d.find_element(By.XPATH, "//div[@role='dialog']//div[@role='button'][contains(., 'Add') or contains(., 'Upload')]")
                dropzone.click()
                time.sleep(2)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
            except Exception:
                pass

        # STEP 1: Click First Next (Create Post Screen)
        print("[FB] Step 3: Uploading and clicking Step 1 'Next'...")
        time.sleep(10)
        try:
            next_1 = wait.until(EC.element_to_be_clickable((
                By.XPATH, 
                "//div[@role='dialog']//div[@aria-label='Next' and @role='button'] | //div[@role='dialog']//button[contains(., 'Next')]"
            )))
            d.execute_script("arguments[0].click();", next_1)
            print("[FB] Step 1 Next button clicked.")
        except Exception as e:
            print(f"[FB] Step 1 Next notice: {e}")

        # STEP 2: Edit Reel Screen (Tags & Step 2 Next)
        print("[FB] Step 4: Edit Reel Screen...")
        time.sleep(5)

        tags_list = re.findall(r"#\w+", caption) if caption else []
        if tags_list:
            try:
                tags_input = wait.until(EC.presence_of_element_located((
                    By.XPATH, 
                    "//input[contains(@placeholder, 'Add tags') or @aria-label='Add tags'] | //div[@role='dialog']//input[@type='text']"
                )))
                actions.move_to_element(tags_input).click().perform()
                time.sleep(0.5)
                for tag in tags_list:
                    clean_tag = tag.replace("#", "")
                    tags_input.send_keys(clean_tag)
                    time.sleep(0.5)
                    tags_input.send_keys(Keys.ENTER)
                    time.sleep(0.5)
                print(f"[FB] Tags added: {tags_list}")
            except Exception as tag_err:
                print(f"[FB] Tags insertion issue: {tag_err}")

        time.sleep(2)

        # Click Step 2 Next Button
        try:
            next_2_selectors = [
                "//div[@role='dialog']//div[@aria-label='Next' and @role='button']",
                "//div[@role='dialog']//span[text()='Next']/ancestor::div[@role='button']",
                "//div[@role='dialog']//button[contains(., 'Next')]"
            ]
            for n_xpath in next_2_selectors:
                elements = d.find_elements(By.XPATH, n_xpath)
                clicked_next = False
                for el in elements:
                    if el.is_displayed():
                        d.execute_script("arguments[0].click();", el)
                        print("[FB] Step 2 Next clicked!")
                        clicked_next = True
                        break
                if clicked_next:
                    break
        except Exception as e:
            print(f"[FB] Step 2 Next error: {e}")

        # STEP 3: Reel Settings -> Click Field First -> Paste -> Click Post
        print("[FB] Step 5: Handling Reel Settings Screen...")
        time.sleep(5)

        if caption:
            try:
                caption_filled = False
                desc_selectors = [
                    "//div[@role='dialog']//div[contains(@aria-label, 'Describe your reel')]",
                    "//div[contains(text(), 'Describe your reel')]/ancestor::div[contains(@class, 'x1')]//div[@contenteditable='true']",
                    "//div[@role='dialog']//div[@contenteditable='true'][@role='textbox']",
                    "//div[@role='dialog']//div[@contenteditable='true']"
                ]

                target_box = None
                for sel in desc_selectors:
                    boxes = d.find_elements(By.XPATH, sel)
                    for b in boxes:
                        if b.is_displayed():
                            target_box = b
                            break
                    if target_box:
                        break

                if target_box:
                    print("[FB] 'Describe your reel' box mil gaya, physical click kar rahe hain...")
                    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_box)
                    time.sleep(1)

                    # 1. ActionChains ke sath physical click taake cursor box ke andar blink kare
                    actions.move_to_element(target_box).click().perform()
                    time.sleep(1)
                    d.execute_script("arguments[0].focus();", target_box)
                    time.sleep(1)

                    # 2. Clipboard update aur Ctrl + V paste
                    pyperclip.copy(caption)
                    time.sleep(0.5)

                    if pyautogui:
                        pyautogui.hotkey('ctrl', 'v')
                        print("[FB] PyAutoGUI se Ctrl+V trigger kiya gaya!")
                    else:
                        target_box.send_keys(Keys.CONTROL, 'v')

                    time.sleep(1)
                    # Verification check: agar khali ho toh send_keys direct chala dein
                    box_text = target_box.text or target_box.get_attribute("textContent") or ""
                    if not box_text.strip():
                        print("[FB] Paste fallback: Direct send_keys enter kar rahe hain...")
                        target_box.send_keys(caption)

                    print("[FB] Caption successfully paste ho gaya!")
                    caption_filled = True
                else:
                    print("[FB] Warning: 'Describe your reel' element locate nahi hua.")

            except Exception as e:
                print(f"[FB] Caption click/paste issue: {e}")

        time.sleep(3)

        # 3. Final Blue "Post" Button Click
        print("[FB] Step 6: Final 'Post' button locate aur click kar rahe hain...")
        post_selectors = [
            "//div[@role='dialog']//div[@aria-label='Post' and @role='button']",
            "//div[@role='dialog']//span[text()='Post']/ancestor::div[@role='button']",
            "//div[@role='dialog']//button[contains(., 'Post')]",
            "//div[@aria-label='Post']"
        ]

        post_clicked = False
        for p_xpath in post_selectors:
            p_elements = d.find_elements(By.XPATH, p_xpath)
            for p_btn in p_elements:
                if p_btn.is_displayed():
                    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", p_btn)
                    time.sleep(1)
                    # Physical mouse click + JS click backup
                    try:
                        actions.move_to_element(p_btn).click().perform()
                    except Exception:
                        pass
                    d.execute_script("arguments[0].click();", p_btn)
                    print("[FB] Final 'Post' button successfully click ho gaya!")
                    post_clicked = True
                    break
            if post_clicked:
                break

    except Exception as ex:
        print(f"[FB ERROR] Major exception: {ex}")

# -------------------------------------------------------------
# 2. TIKTOK STUDIO AUTOMATION
# -------------------------------------------------------------
def run_tiktok(video_path, caption):
    try:
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
                btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                d.execute_script("arguments[0].click();", btn)
                break
            except Exception:
                continue

        time.sleep(2)
        for xp in ["//button[normalize-space()='Post now']", "//button[contains(., 'Post now')]", "//div[@role='dialog']//button[contains(., 'Post now')]"]:
            try:
                p_btn = WebDriverWait(d, 6).until(EC.element_to_be_clickable((By.XPATH, xp)))
                d.execute_script("arguments[0].click();", p_btn)
                break
            except Exception:
                pass
    except Exception as ex:
        print(f"[TIKTOK ERROR]: {ex}")

# -------------------------------------------------------------
# 3. YOUTUBE STUDIO AUTOMATION
# -------------------------------------------------------------
def run_youtube(video_path, caption):
    try:
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
    except Exception as ex:
        print(f"[YOUTUBE ERROR]: {ex}")

# -------------------------------------------------------------
# 4. INSTAGRAM WEB AUTOMATION
# -------------------------------------------------------------
def run_instagram(video_path, caption):
    try:
        d = get_driver()
        d.get("https://www.instagram.com")
        wait = WebDriverWait(d, 30)
        bypass_common_popups(d)

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
        print(f"[INSTAGRAM ERROR]: {e}")

# -------------------------------------------------------------
# FLASK WEB DASHBOARD BACKEND
# -------------------------------------------------------------
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
        return jsonify({"status": "error", "message": "Video file ka path durust nahi hai ya file maujood nahi hai!"})

    targets = {
        "tiktok": run_tiktok,
        "facebook": run_facebook_page,
        "youtube": run_youtube,
        "instagram": run_instagram
    }

    func = targets.get(platform)
    if not func:
        return jsonify({"status": "error", "message": "Platform unknown!"})

    threading.Thread(target=func, args=(video_path, caption), daemon=True).start()
    return jsonify({"status": "success", "message": f"{platform.upper()} automated publish sequence shuru ho chuki hai!"})

if __name__ == '__main__':
    print("Serving on http://localhost:5000")
    app.run(port=5000, debug=False)