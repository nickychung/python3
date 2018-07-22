# coding=big5

from PIL import Image
from PIL import ImageEnhance
import PIL.ImageOps
import pytesseract
import sys
import platform
import time
from multiprocessing.connection import FAILURE
from _msi import PID_LASTAUTHOR

print("Python EXE     : " + sys.executable)
print("Architecture   : " + platform.architecture()[0])

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

timeslots = ['08:30 - 10:30','10:31 - 12:30','14:00 - 16:30']


lastAttempCode = 'KF622588'
#lastAttempCode = 'HF082008' #old code
byear = '1992'
bmonth = '03'
bday = '19'
teleNo = '62772343'
wearClasses = False
testArea = '2' #1=香港  2=九龍或新界



#lastAttempCode = 'HC085250'
#===============================================================================
# lastAttempCode = 'KC274345'
# byear = '1975'
# bmonth = '07'
# bday = '09'
# teleNo = '94063065'
# wearClasses = True
# testArea = '2'
#===============================================================================

def get_captcha(driver, element, path):
    # now that we have the preliminary stuff out of the way time to get that image :D
    location = element.location
    size = element.size
    # saves screenshot of entire page
    
    #w = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
    #h = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
    #driver.manage.window.resize_to(w+100, h+100)
    driver.save_screenshot(path)

    # uses PIL library to open image in memory
    image = Image.open(path)
    left = location['x']
    #top = location['y']
    top = 530
    right = location['x'] + size['width']
    #bottom = location['y'] + size['height']
    bottom = 530 + 75
    image = image.crop((left, top, right, bottom))  # defines crop points
    print(image)
    
    
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--image", required=True,
    #help="path to input image to be OCR'd")
    #args = vars(ap.parse_args())
    image = image.convert('RGB')
    image = PIL.ImageOps.invert(image)
    image = ImageEnhance.Brightness(image)
    image = image.enhance(5)
    #imageArray = numpy.array(image)
    #imageArray = imageArray[:, :, ::-1].copy()
    
    #filename = "{}.png".format(os.getpid())
    #image.save(filename)
    #image.show()

    return image
    #image.save(path, 'png')  # saves new cropped image
    #print(image)

def try_captcha(driver,img):
    image = get_captcha(driver, img, "captcha.png")
    text = pytesseract.image_to_string(image, config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz --psm 7 -l eng textord_space_size_is_variable 1")
    text = ''.join(text.split())
    print("text:", text)
    txtInput = driver.find_element_by_xpath("//input[@type='text']")
    txtInput.send_keys(text)
    driver.find_element_by_link_text("繼續").click()
    
    
    return 0

def fluent_wait_page_four(driver,ldelay):
    try:
        WebDriverWait(driver, ldelay).until(EC.presence_of_element_located((By.NAME, "main")))
        return 1
    except TimeoutException:
        return 0
    
def fluent_wait_page_five(driver,ldelay):
    try:
        WebDriverWait(driver, ldelay).until(EC.presence_of_element_located((By.NAME, "testAreaCode")))
        return 1
    except TimeoutException:
        return 0
    

def call_page_one():
    tries = 1
    maxInitialRetry = 15
    page_one_delay = 10
    while tries <= maxInitialRetry:
        try:
            dv = webdriver.Chrome()
            dv.set_page_load_timeout(page_one_delay)
            #dv.set_network_conditions(latency=500,download_throughput=0.1 * 1024,upload_throughput=0.1 * 1024) #NETWORK THROTTLING in kb/s
            dv.get("https://eapps1.td.gov.hk/repoes/td-es-app517/Welcome.do?language=zh")
            assert "SC-517" in dv.title
            #dv.get("https://www.google.com")
            dv.find_element_by_css_selector("input[type='radio'][value='retas']").click()
            dv.find_element_by_link_text("下一頁").click()
            #dv.set_page_load_timeout(0)
            break
        except TimeoutException:
            print("Can't load page one - retry:{}".format(tries))
            if(tries == maxInitialRetry):
                sys.exit()
            tries = tries + 1
            dv.close()
        except AssertionError:
            print("Assertion Error (Page maintenance?)")
            tries = maxInitialRetry
            dv.close()
            sys.exit
            return False
            
    return dv
#elem = driver.find_element_by_name("serviceChoice")

retries = 1 
delay = 6 # seconds
maxRetry = 10
p3retries = 1
driver = call_page_one()
try:
    while (retries <= maxRetry and driver):
        WebDriverWait(driver,delay).until(EC.presence_of_all_elements_located((By.ID,'contentPanel')))
        print("2nd Page is ready!")
        appointment_button = driver.find_element_by_css_selector("input[type='radio'][value='appointment']")
        if(appointment_button.is_enabled()):
            appointment_button.click()
            driver.find_element_by_link_text("開始").click()
            retries = maxRetry
        else:
            if(retries < maxRetry):
                driver.close()
                time.sleep(1)
                driver = call_page_one()
            else:
                print("max:{}".format(maxRetry) + " retries")
        retries = retries + 1
        #driver.set_network_conditions(latency=500,download_throughput=0.1 * 1024,upload_throughput=0.1 * 1024) #NETWORK THROTTLING in kb/s
        
        if(retries >= maxRetry):
            print("entering page 3")
            try:
                WebDriverWait(driver,delay).until(EC.presence_of_all_elements_located((By.ID,'contentPanel')))
                print("3rd Page is ready!")
            except TimeoutException:
                driver.close()
                time.sleep(1)
                driver = call_page_one()
                if(p3retries <= maxRetry):
                    retries = 1
                p3retries = p3retries + 1    
                print("2 Loading took too much time!")   
    
    
    #driver.set_network_conditions(latency=500,download_throughput=1 * 1024,upload_throughput=1 * 1024) #NETWORK THROTTLING in kb/s


    if(driver):
        for x in range(19): 
            if(fluent_wait_page_four(driver, 0.5) == 1):
                
                driver.switch_to.frame(driver.find_element_by_name('main'))
                print("page 4 starts...")
                
                WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,'testFormNumForLastAttempt')))
                try:
                #driver.find_element_by_xpath("//div[@class='pageTitle'][contains(text(),'預約重考生快期')]")
                    driver.find_element_by_id('testFormNumForLastAttempt').send_keys(lastAttempCode)
                    driver.find_element_by_id('testFormBirthYear').send_keys(byear)
                    driver.find_element_by_id('testFormBirthMonth').send_keys(bmonth)
                    driver.find_element_by_id('testFormBirthDay').send_keys(bday)
                    driver.find_element_by_link_text("繼續").click()
            
                    driver.find_element_by_name('telephoneNo').send_keys(teleNo)
                    if(wearClasses):
                        driver.find_element_by_css_selector("input[type='radio'][name='wearLensesInd'][value='Y']").click()
                    else:
                        driver.find_element_by_css_selector("input[type='radio'][name='wearLensesInd'][value='N']").click()
                    driver.find_element_by_css_selector("input[type='radio'][name='wearAidsInd'][value='N']").click()
                    driver.find_element_by_css_selector("input[type='radio'][name='physicalHandicapInd'][value='N']").click()
                    driver.find_element_by_link_text("繼續").click()     
                except TimeoutException:
                    driver.quit()    
                break                                                                            
            else:
                imgs = driver.find_elements_by_tag_name("img") #find the captcha image element and store it in parameter img
                for img in imgs:
                    img_src = img.get_attribute('src')
                    if "jcaptcha" in img_src:
                        myCaptcha = img
                        print(img_src)
                        break                                                                 
                driver.find_element_by_css_selector("input[type='checkbox'][value='on']").click()
                driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
                try_captcha(driver, myCaptcha)

    if(driver):
        
        #for x in range(19): 
            if(fluent_wait_page_five(driver, 0.5) == 1):
                sl = Select(driver.find_element_by_id('testAreaCode'))
                print("page 5 starts...")
                if(testArea == '1'):
                    sl.select_by_value('1')
                else:
                    sl.select_by_value('2')
                #driver.switch_to.frame(driver.find_element_by_name('main'))
                sl = Select(driver.find_element_by_id('timeslotSession'))
                for tsl in timeslots:
                    #print(tsl)
                    sl.select_by_value(tsl)
                    try:
                        link = driver.find_element_by_link_text('1')
                        link.click()
                    except NoSuchElementException:
                        print("no such element")
                    time.sleep(2)
                    sl = Select(driver.find_element_by_id('timeslotSession')) #Select need to reassign after one session, since the page is refreshed
                         
                

except TimeoutException:
    print("1 Loading took too much time!")                
            #WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "warning")))
            #print("found warning")
            #WebDriverWait(driver, delay)
           
        
        
        
        #except TimeoutException:
            #print("4th Page is ready!")
            
            #driver.switch_to.frame(driver.find_element_by_name('main'))
            #driver.find_element_by_xpath("//div[@class='pageTitle'][contains(text(),'預約重考生快期')]")
            
            
            #driver.find_element_by_id('testFormNumForLastAttempt').send_keys(lastAttempCode)
            #driver.find_element_by_id('testFormBirthYear').send_keys(byear)
            #driver.find_element_by_id('testFormBirthMonth').send_keys(bmonth)
            #driver.find_element_by_id('testFormBirthDay').send_keys(bday)
            #driver.find_element_by_link_text("繼續").click()
            
            #driver.find_element_by_name('telephoneNo').send_keys(teleNo)
            #driver.find_element_by_css_selector("input[type='radio'][name='wearLensesInd'][value='Y']").click()
            #driver.find_element_by_css_selector("input[type='radio'][name='wearAidsInd'][value='N']").click()
            #driver.find_element_by_css_selector("input[type='radio'][name='physicalHandicapInd'][value='N']").click()
            #driver.find_element_by_link_text("繼續").click()
            #<input type="radio" name="wearLensesInd" 
            #value="Y" onclick="onWearLensesIndClick(this.value)" autocomplete="off">
           
            
            #txtinputs.
            
            #<input type="text" size="10" maxlength="8" 
            #name="testFormNumForLastAttempt" id="testFormNumForLastAttempt" 
            #value="" class="uppercase" autocomplete="off">
            
        
        
        #gray = cv.LoadImage('jcaptcha', cv.CV_LOAD_IMAGE_GRAYSCALE)
        #urllib.request.urlretrieve("https://eapps1.td.gov.hk/repoes/td-es-app517/jcaptcha", "local.jpg")
        #image_ocr = Image.open("captcha.png")
        #text = pytesseract.image_to_string(image_ocr)
        #print(text)
       
        
        #cv.Threshold(gray, gray, 231, 255, cv.CV_THRESH_BINARY)
        #api = tesseract.TessBaseAPI()
        #api.Init(".","eng",tesseract.OEM_DEFAULT)
        #api.SetVariable("tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyz")
        #api.SetPageSegMode(tesseract.PSM_SINGLE_WORD)
        #tesseract.SetCvImage(gray,api)
        #print(api.GetUTF8Text())
        #time.sleep(3)
        #driver.quit()
        #sys.exit()

#elem = driver.find_element(By.id("serviceChoice:retas"))
#elem.click()
#elem.send_keys("pycon")
#elem.send_keys(Keys.RETURN)
#assert "No results found." not in driver.page_source
#driver.close()

