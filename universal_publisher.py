import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip

try:
    import pyautogui
except ImportError:
    pyautogui = None

driver = None

def get_driver():
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument(r"--user-data-dir=C:\Users\princ\AppData\Local\Google\Chrome\User Data")
        options.add_argument(r"--profile-directory=Default")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
    return driver

def bypass_common_popups(d):
    """Closes common overlay modals across all platforms."""
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
            elements = d.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    d.execute_script("arguments[0].click();", el)
                    time.sleep(1)
        except Exception:
            pass

def validate_inputs():
    path = video_path_entry.get().strip()
    cap = caption_text.get("1.0", tk.END).strip()
    if not path:
        messagebox.showwarning("Warning", "Pehle video file select kijiye!")
        return None, None
    if not os.path.exists(path):
        messagebox.showerror("Error", "Video file ka path durust nahi hai!")
        return None, None
    return path, cap

# -------------------------------------------------------------
# 1. TIKTOK AUTO PUBLISH
# -------------------------------------------------------------
def process_tiktok():
    path, cap = validate_inputs()
    if not path:
        return
    try:
        d = get_driver()
        d.get("https://www.tiktok.com/tiktokstudio/upload")
        wait = WebDriverWait(d, 35)
        
        time.sleep(4)
        bypass_common_popups(d)
        
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(path)
        print("TikTok: Video file send ho gayi.")
        
        if cap:
            try:
                caption_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".public-DraftEditor-content, div[contenteditable='true']")))
                caption_box.send_keys(cap)
                print("TikTok: Caption enter ho gaya.")
            except Exception as e:
                print(f"Caption Box Notice: {e}")
                
        print("Waiting for upload and popups...")
        time.sleep(10)
        bypass_common_popups(d)
        
        d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        post_button_xpaths = [
            "//button[normalize-space()='Post']",
            "//button[contains(@class, 'btn-post')]",
            "//div[contains(@class, 'btn-post')]//button",
            "//button[contains(., 'Post')]"
        ]
        
        for xpath in post_button_xpaths:
            try:
                post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                d.execute_script("arguments[0].scrollIntoView(true);", post_btn)
                time.sleep(1)
                d.execute_script("arguments[0].click();", post_btn)
                print("TikTok: Post button clicked.")
                break
            except Exception:
                continue
                
        time.sleep(2)
        post_now_xpaths = [
            "//button[normalize-space()='Post now']",
            "//button[contains(., 'Post now')]",
            "//div[@role='dialog']//button[contains(., 'Post now')]"
        ]
        for xpath in post_now_xpaths:
            try:
                post_now_btn = WebDriverWait(d, 6).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                d.execute_script("arguments[0].click();", post_now_btn)
                print("TikTok: 'Post now' confirmation clicked!")
                break
            except Exception:
                continue
                
        messagebox.showinfo("TikTok", "TikTok video process trigger ho chuka hai!")
    except Exception as ex:
        messagebox.showerror("TikTok Error", f"TikTok process mein masla aya: {ex}")

# -------------------------------------------------------------
# 2. META BUSINESS SUITE AUTO PUBLISH
# -------------------------------------------------------------
def process_meta():
    path, cap = validate_inputs()
    if not path:
        return
    try:
        d = get_driver()
        d.get("https://business.facebook.com/latest/composer")
        wait = WebDriverWait(d, 35)
        
        time.sleep(5)
        bypass_common_popups(d)
        
        pyperclip.copy(os.path.abspath(path))
        time.sleep(1)

        uploaded = False
        all_inputs = d.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for inp in all_inputs:
            try:
                d.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", inp)
                inp.send_keys(os.path.abspath(path))
                print("Meta: Direct file input attach ho gaya.")
                uploaded = True
                break
            except Exception:
                continue

        if not uploaded:
            try:
                add_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH, 
                    "//div[@role='button'][contains(., 'Add photo/video')] | //button[contains(., 'Add photo/video')]"
                )))
                d.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
                time.sleep(1)
                add_btn.click()
                time.sleep(2)

                menu_opts = d.find_elements(By.XPATH, "//*[@role='menuitem' or @role='button'][contains(., 'Upload from desktop') or contains(., 'Upload video')]")
                if menu_opts:
                    for opt in menu_opts:
                        if opt.is_displayed():
                            opt.click()
                            time.sleep(2)
                            break

                if pyautogui:
                    time.sleep(1.5)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    print("Meta: Windows File Picker se file attach ho gayi.")
            except Exception as click_err:
                print(f"Meta click flow notice: {click_err}")

        time.sleep(3)
        if cap:
            try:
                text_box = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    "div[contenteditable='true'][role='textbox'], div[contenteditable='true']"
                )))
                d.execute_script("arguments[0].scrollIntoView({block: 'center'});", text_box)
                text_box.click()
                time.sleep(1)
                text_box.send_keys(cap)
                print("Meta: Text successfully enter ho gaya.")
            except Exception as e:
                print(f"Meta caption box issue: {e}")

        print("Meta: 'Processing media' check ho raha hai...")
        for _ in range(60):
            processing_elements = d.find_elements(By.XPATH, "//*[contains(text(), 'Processing media')]")
            if any(el.is_displayed() for el in processing_elements):
                time.sleep(2)
            else:
                break
                
        publish_clicked = False
        for _ in range(25):
            bypass_common_popups(d)
            try:
                publish_btn = d.find_element(By.XPATH, "//div[@aria-label='Publish' or @aria-label='Post' or contains(text(), 'Publish')][not(@aria-disabled='true') and not(contains(@class, 'disabled'))]")
                if publish_btn.is_displayed():
                    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", publish_btn)
                    time.sleep(1.5)
                    d.execute_script("arguments[0].click();", publish_btn)
                    print("Meta: Solid Blue Publish button click ho gaya!")
                    publish_clicked = True
                    break
            except Exception:
                pass
            time.sleep(2)

        if publish_clicked:
            messagebox.showinfo("Meta", "Meta Business Suite par media processing mukammal ho kar Publish trigger ho chuka hai!")
        else:
            messagebox.showinfo("Meta", "Media aur caption add ho chuke hain.")

    except Exception as ex:
        messagebox.showerror("Meta Error", f"Meta upload mein masla aya: {ex}")

# -------------------------------------------------------------
# 3. YOUTUBE STUDIO EXACT SEQUENCE AUTO PUBLISH
# -------------------------------------------------------------
def process_youtube():
    path, cap = validate_inputs()
    if not path:
        return
    try:
        d = get_driver()
        d.get("https://studio.youtube.com")
        wait = WebDriverWait(d, 35)
        
        time.sleep(4)
        bypass_common_popups(d)
        
        # Step 1: Open Upload Dialog via 'Create' or 'Upload videos'
        try:
            create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-icon")))
            create_btn.click()
            time.sleep(1.5)
            upload_btn = wait.until(EC.element_to_be_clickable((By.ID, "text-item-0")))
            upload_btn.click()
        except Exception:
            try:
                upload_center_btn = d.find_element(By.XPATH, "//ytcp-button[@id='upload-button'] | //button[contains(., 'Upload videos')]")
                upload_center_btn.click()
            except Exception as e:
                print(f"YouTube open dialog issue: {e}")

        time.sleep(2)
        
        # Step 2: Attach Video File
        uploaded = False
        try:
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(os.path.abspath(path))
            print("YouTube: File input direct attach ho gaya.")
            uploaded = True
        except Exception:
            pass

        if not uploaded:
            pyperclip.copy(os.path.abspath(path))
            try:
                select_files_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Select files')] | //button[contains(., 'Select files')]")))
                select_files_btn.click()
                time.sleep(2)
                if pyautogui:
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    print("YouTube: Windows dialog se file paste ho gayi.")
            except Exception as e:
                print(f"YouTube select files error: {e}")

        # Step 3: Fill Details (Title/Description) & 'Not made for kids'
        print("YouTube: Details screen load ho rahi hai...")
        time.sleep(6)
        
        if cap:
            try:
                textboxes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#textbox")))
                if len(textboxes) > 1:
                    d.execute_script("arguments[0].scrollIntoView({block: 'center'});", textboxes[1])
                    textboxes[1].click()
                    time.sleep(0.5)
                    textboxes[1].send_keys(cap)
                    print("YouTube: Description enter ho gayi.")
            except Exception as e:
                print(f"YouTube description warning: {e}")

        # Select 'No, it's not made for kids'
        try:
            not_for_kids = wait.until(EC.element_to_be_clickable((
                By.XPATH, 
                "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK'] | //div[contains(text(), 'No, it')]/ancestor::tp-yt-paper-radio-button"
            )))
            d.execute_script("arguments[0].scrollIntoView({block: 'center'});", not_for_kids)
            time.sleep(1)
            not_for_kids.click()
            print("YouTube: 'No, it's not made for kids' select ho gaya.")
        except Exception as e:
            print(f"Audience option notice: {e}")

        # Step 4: Step through Wizard (Details -> Video elements -> Checks -> Visibility)
        for step in range(3):
            time.sleep(2)
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.ID, "next-button")))
                d.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                next_btn.click()
                print(f"YouTube: Next button step {step + 1} clicked.")
            except Exception as e:
                print(f"Next button issue at step {step + 1}: {e}")
                break

        # Step 5: Visibility Screen -> Select 'Public'
        time.sleep(2)
        try:
            public_radio = wait.until(EC.element_to_be_clickable((
                By.XPATH, 
                "//tp-yt-paper-radio-button[@name='PUBLIC'] | //span[contains(text(), 'Public')]/ancestor::tp-yt-paper-radio-button"
            )))
            d.execute_script("arguments[0].scrollIntoView({block: 'center'});", public_radio)
            time.sleep(1)
            public_radio.click()
            print("YouTube: 'Public' radio button select ho gaya.")
        except Exception as e:
            print(f"Public radio notice: {e}")

        # Step 6: Click Final Publish Button
        time.sleep(2)
        publish_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, 
            "//ytcp-button[@id='done-button'] | //div[contains(text(), 'Publish')]/ancestor::ytcp-button"
        )))
        d.execute_script("arguments[0].scrollIntoView({block: 'center'});", publish_btn)
        time.sleep(1)
        publish_btn.click()
        print("YouTube: Final Publish button clicked successfully!")

        messagebox.showinfo("YouTube", "YouTube video kamyabi se upload aur Publish ho chuki hai!")

    except Exception as ex:
        messagebox.showerror("YouTube Error", f"YouTube automation sequence mein masla aya: {ex}")

# -------------------------------------------------------------
# 4. INSTAGRAM AUTO PUBLISH
# -------------------------------------------------------------
def process_instagram():
    path, cap = validate_inputs()
    if not path:
        return
    try:
        d = get_driver()
        d.get("https://www.instagram.com")
        wait = WebDriverWait(d, 30)
        
        bypass_common_popups(d)
        
        svg_new_post = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='New post'], svg[aria-label='Nayi post']")))
        svg_new_post.find_element(By.XPATH, "./ancestor::a | ./ancestor::div[contains(@role, 'button')]").click()
        time.sleep(3)
        
        bypass_common_popups(d)
        
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        file_input.send_keys(path)
        time.sleep(8)
        
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Aage')]")))
        next_btn.click()
        time.sleep(3)
        
        next_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Next' or text()='Aage')]")))
        next_btn2.click()
        time.sleep(3)
        
        if cap:
            try:
                caption_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Write a caption...'], div[contenteditable='true']")))
                caption_area.send_keys(cap)
                time.sleep(2)
            except Exception:
                pass
                
        share_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Share' or text()='Sajha karein')]")))
        share_btn.click()
        
        messagebox.showinfo("Instagram", "Instagram par post share hone lag gayi hai!")
    except Exception as ex:
        messagebox.showerror("Instagram Error", f"Instagram error: {ex}")

def select_video():
    filename = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.mov *.avi")])
    if filename:
        video_path_entry.delete(0, tk.END)
        video_path_entry.insert(0, filename)

# --- GUI INTERFACE ---
root = tk.Tk()
root.title("Biya's Multi-Platform Auto Publisher 🚀")
root.geometry("650x590")
root.resizable(False, False)

tk.Label(root, text="Select Video File (.mp4):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
frame_vid = tk.Frame(root)
frame_vid.pack(fill="x", padx=20)

video_path_entry = tk.Entry(frame_vid, width=54, font=("Arial", 10))
video_path_entry.pack(side=tk.LEFT, padx=(0, 10))

browse_btn = tk.Button(frame_vid, text="Browse", command=select_video, bg="#007ACC", fg="white", font=("Arial", 9, "bold"))
browse_btn.pack(side=tk.LEFT)

tk.Label(root, text="Caption / Description / Tags:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
caption_text = tk.Text(root, height=6, width=66, font=("Arial", 10))
caption_text.pack(padx=20)

tk.Label(root, text="Click Platform to Auto-Fill, Bypass Popups & Publish:", font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

btn_frame = tk.Frame(root)
btn_frame.pack(fill="both", expand=True, padx=20, pady=5)

tiktok_btn = tk.Button(btn_frame, text="1. Auto Publish to TikTok 🎵", command=process_tiktok, bg="#010101", fg="white", font=("Arial", 10, "bold"), height=2)
tiktok_btn.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

meta_btn = tk.Button(btn_frame, text="2. Auto Publish to Meta Suite 🔵", command=process_meta, bg="#1877F2", fg="white", font=("Arial", 10, "bold"), height=2)
meta_btn.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

yt_btn = tk.Button(btn_frame, text="3. Auto Publish to YouTube 🔴", command=process_youtube, bg="#FF0000", fg="white", font=("Arial", 10, "bold"), height=2)
yt_btn.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

insta_btn = tk.Button(btn_frame, text="4. Auto Publish to Instagram 📸", command=process_instagram, bg="#E1306C", fg="white", font=("Arial", 10, "bold"), height=2)
insta_btn.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

btn_frame.grid_columnconfigure(0, weight=1)
btn_frame.grid_columnconfigure(1, weight=1)

root.mainloop()