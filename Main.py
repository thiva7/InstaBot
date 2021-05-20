from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import threading
import random
import re


def check_Url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('main.ui', self)  # Load the .ui file
        self.Init_Ui()

    def load_json(self):
        with open('data.json') as json_file:
            data = json.load(json_file)
        return data

    def Init_Ui(self):
        self.show()
        self.saveBtn.clicked.connect(self.saveSettings)
        data = self.load_json()
        # set text to form , from saved to Joson
        for p in data['login']:
            username = self.username.setText(p['username'])
            self.password.setText(p['password'])
        for p in data['comments']:
            self.wait.setText(p['waitTime'])
            self.comment.setText("\n".join(map(str, p['comment'])))
            self.url.setPlainText("\n".join(map(str, p['url'])))
            self.hashtags.setPlainText("\n".join(map(str, p['hashtags'])))
            self.profile.setText(p['profile'])
            if p['do_comment'] == 'yes':
                self.checkBoxDoComment.setChecked(True)
        for p in data['like']:
            self.numLikes.setText(str(p['numLikes']))
            if p['like'] == 'yes':
                self.LikecheckBox.setChecked(True)
        self.runBtn.clicked.connect(self.run_bot)
        # CheckBoxs
        self.runWithUrlsCheckBox.stateChanged.connect(self.uncheck)
        self.checkBoxHashTags.stateChanged.connect(self.uncheck)
        self.checkBoxProfile.stateChanged.connect(self.uncheck)

        self.msg.setText('')

    def uncheck(self, state):
        # checking if state is checked
        if state == Qt.Checked:
            # if first check box is selected
            if self.sender() == self.checkBoxHashTags:
                # making other check box to uncheck
                self.runWithUrlsCheckBox.setChecked(False)
                self.checkBoxProfile.setChecked(False)

                # if second check box is selected
            elif self.sender() == self.runWithUrlsCheckBox:

                # making other check box to uncheck
                self.checkBoxHashTags.setChecked(False)
                self.checkBoxProfile.setChecked(False)

            elif self.sender() == self.checkBoxProfile:

                self.runWithUrlsCheckBox.setChecked(False)
                self.checkBoxHashTags.setChecked(False)


    def login(self):
        data = self.load_json()

        for p in data['login']:
            username = p['username']
            password = p['password']
        self.driver = webdriver.Firefox()
        self.driver.get("https://instagram.com/?hl=en")
        sleep(3)

        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/button[1]').click()
        sleep(3)
        self.driver.find_element_by_xpath("//input[@name=\"username\"]") \
            .send_keys(username)
        sleep(2)
        self.driver.find_element_by_xpath("//input[@name=\"password\"]") \
            .send_keys(password)
        sleep(2)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div').click()
        sleep(3)

    def notifications(self):
        self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/div/div/button").click()
        sleep(5)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Όχι τώρα' )]").click()


    def HashTags(self):
        data = self.load_json()
        for c in data['comments']:
            for h in c['hashtags']:
                hashtag = h
                self.driver.get(f'https://www.instagram.com/explore/tags/{hashtag}/?hl=en')

                # Click first thumbnail to open
                first_thumbnail = self.driver.find_element_by_xpath(
                    "//*[@id='react-root']/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]")
                first_thumbnail.click()
                sleep(3)
                for l in data['like']:
                    NumLikes = l['numLikes']
                    for post in range(0, NumLikes):
                        sleep(3)
                        # Do comment
                        if self.checkBoxDoComment.isChecked():
                            comment = ((data["comments"][0])['comment'])
                            com = random.choice(comment)
                            self.driver.find_element_by_xpath("//textarea").click()
                            sleep(3)
                            self.driver.find_element_by_xpath("//textarea").send_keys(com)
                            # add submit to comment
                            self.driver.find_element_by_xpath("//button[contains(text(), 'Post' )]").click()
                        sleep(5)
                        if l['like'] == "yes":
                            self.driver.find_element_by_xpath(
                                "/html/body/div/div[2]/div/article/div[3]/section[1]/span[1]/button").click()
                            sleep(5)

                        self.driver.find_element_by_link_text('Next').click()

    def Urls(self):
        data = self.load_json()
        for c in data['comments']:
            for h in c['url']:
                url = h
                self.driver.get(f'{url}?hl=en')
                sleep(3)
                # check Likes for Specific Urls

                if self.checkBoxDoComment.isChecked():
                    comment = ((data["comments"][0])['comment'])
                    com = random.choice(comment)
                    self.driver.find_element_by_xpath(
                        "/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[3]/div/form/textarea") \
                        .click()
                    sleep(3)
                    self.driver.find_element_by_xpath(
                        "/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[3]/div/form/textarea") \
                        .send_keys(com)
                    # add submit to comment
                    self.driver.find_element_by_xpath("//button[contains(text(), 'Post' )]").click()

                sleep(5)
                for like in data['like']:
                    if like['like'] == "yes":
                        self.driver.find_element_by_xpath(
                            "/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]").click()
                sleep(5)

    def profile_url(self):
        data = self.load_json()
        for c in data['comments']:
            url = c['profile']
            self.driver.get(f'{url}?hl=en')
            # Click first thumbnail to open
            first_thumbnail = self.driver.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/div[3]/article/div[1]/div/div[1]/div[1]")
            first_thumbnail.click()
            for l in data['like']:
                NumLikes = l['numLikes']
                for post in range(0, NumLikes):
                    sleep(3)
                    # Do comment
                    if self.checkBoxDoComment.isChecked():
                        comment = ((data["comments"][0])['comment'])
                        com = random.choice(comment)
                        self.driver.find_element_by_xpath("//textarea").click()
                        sleep(3)
                        self.driver.find_element_by_xpath("//textarea").send_keys(com)
                        sleep(5)
                        self.driver.find_element_by_xpath("//button[contains(text(), 'Post' )]").click()
                    sleep(5)
                    if l['like'] == "yes":
                        self.driver.find_element_by_xpath(
                            "/html/body/div/div[2]/div/article/div[3]/section[1]/span[1]/button").click()
                        sleep(5)

                    self.driver.find_element_by_link_text('Next').click()





    def run_bot(self):
        likes = 0


        self.login()
        sleep(5)

        self.notifications()
        sleep(5)

        if self.checkBoxHashTags.isChecked():
            self.HashTags()
        elif self.runWithUrlsCheckBox.isChecked():
            self.Urls()
        else:
            self.profile_url()

        sleep(5)

    def saveSettings(self):
        username = self.username.text()
        password = self.password.text()
        profile = self.profile.text()
        comment = self.comment.toPlainText()
        wait = self.wait.text()
        numLikes = self.numLikes.text()

        url = self.url.toPlainText()
        hashtags = self.hashtags.toPlainText()
        like = self.LikecheckBox.isChecked()

        do_comment = self.checkBoxDoComment.isChecked()
        if like:
            like = 'yes'
        else:
            like = 'no'

        if do_comment:
            do_comment = 'yes'
        else:
            do_comment = 'no'
        if check_Url(profile):
            data = {}
            data['login'] = []
            data['login'].append({
                'username': username,
                'password': password,
            })
            data['comments'] = []
            data['comments'].append({
                'waitTime': wait,
                'url': url.splitlines(),
                'comment': comment.splitlines(),
                'hashtags': hashtags.splitlines(),
                'do_comment': do_comment,
                'profile' : profile
            })
            data['like'] = []
            data['like'].append({
                'like': like,
                'numLikes': int(numLikes)
            })

            self.msg.setText("Settings Saved")
            with open('data.json', 'w') as outfile:
                json.dump(data, outfile)
        else:
            self.msg.setText("Url Is Invalid ,  make sure to include https://")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    app.exec_()
