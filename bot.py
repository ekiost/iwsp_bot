import logging
import os
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from telegram.ext import ContextTypes, Application

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")

current_job_list = {}
driver = None


def get_session_items():
    global driver
    logger.info("Starting API token retrieval process")
    url = "https://readytalent2.singaporetech.edu.sg/"
    try:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        sign_in_button = wait.until(
            ec.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[2]/div/a[2]"))
        )
        sleep(5)
        sign_in_button.click()
        logger.info("Clicked initial sign-in button")

        wait.until(ec.url_changes(driver.current_url))

        username = wait.until(ec.visibility_of_element_located((By.ID, "userNameInput")))
        username.send_keys(USER_NAME)
        logger.info("Entered username")

        password = wait.until(ec.visibility_of_element_located((By.ID, "passwordInput")))
        password.send_keys(PASSWORD)
        logger.info("Entered password")

        sign_in = wait.until(ec.element_to_be_clickable((By.ID, "submitButton")))
        sign_in.click()
        logger.info("Clicked final sign-in button")

        wait.until(ec.presence_of_element_located((By.TAG_NAME, "body")))
        sleep(5)

        api_token = driver.execute_script("return sessionStorage.getItem('apitoken')")
        logger.info("Retrieved API token")

        student_id = driver.execute_script("return sessionStorage.getItem('StudentId')")
        logger.info(f"Retrieved student ID: {student_id}")

        return student_id, api_token
    except Exception as e:
        logger.error(f"Error in get_api_token: {str(e)}")
        return None
    finally:
        driver.quit()
        logger.info("Closed browser")


def get_job_list():
    logger.info("Starting job list retrieval")

    session_items = get_session_items()

    url = f"https://mvw9e7kvt9.execute-api.ap-southeast-1.amazonaws.com/Prod?requestname=LoadJobDetailsStudentDashboard&studentId={session_items[0]}&accessLevelCondition="

    headers = {'apitoken': session_items[1]}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        response_json = response.json()

        job_list = {
            job['sit_jobpostingid']: {
                'job_title': job['sit_name'],
                'company_name': job['acc.name'],
                'allowance': job['sit_allowance@OData.Community.Display.V1.FormattedValue'],
                'number_of_vacancies': job['sit_numberofvacancies']
            } for job in response_json
        }

        logger.info(f"Retrieved {len(job_list)} jobs")
        if (len(job_list) == 0):
            logger.info("Retrieve job list again, as no job found")
            get_job_list()
        return job_list
    except requests.RequestException as e:
        logger.error(f"Error in get_job_list: {str(e)}")
        return {}


def check_job_list():
    logger.info("Checking for new jobs")
    new_job_list = get_job_list()
    global current_job_list
    new_jobs = {job_id: job for job_id, job in new_job_list.items() if job_id not in current_job_list}
    if new_jobs:
        logger.info(f"Found {len(new_jobs)} new jobs")
        current_job_list = new_job_list
    else:
        logger.info("No new jobs found")
    return new_jobs if new_jobs else None


async def notify_new_jobs(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting job notification process")
    new_jobs = check_job_list()
    if new_jobs is None:
        logger.info("No new jobs to notify")
        return

    for job_id, job in new_jobs.items():
        message = (
            f"🆕 New Job Listing 🆕\n"
            f"📝 {job['job_title']}\n"
            f"🏢 {job['company_name']}\n"
            f"💰 {job['allowance']}\n"
            f"👥 {job['number_of_vacancies']}\n"
        )
        try:
            # Replace chat_id with your own chat_id
            await context.bot.send_message(chat_id='@sitnofuture', text=message)
            logger.info(f"Sent notification for job: {job['job_title']}")
            sleep(2)
        except Exception as e:
            logger.error(f"Error sending notification for job {job['job_title']}: {str(e)}")


def main():
    logger.info("Starting application")

    application = Application.builder().token(API_TOKEN).build()
    job_queue = application.job_queue

    # Initial job check to populate current_job_list 
    check_job_list()
    logger.info(f"Initial job check completed successfully with {len(current_job_list)} jobs")

    # Schedule 10-min job to check for new jobs
    logger.info("Scheduling job to check for new jobs every 10 minutes")
    job_queue.run_repeating(notify_new_jobs, interval=600)
    
    application.run_polling()
    logger.info("Application is running")


if __name__ == "__main__":
    main()
