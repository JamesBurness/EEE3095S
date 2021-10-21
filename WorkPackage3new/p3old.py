# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
#===========
import time
#===========

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
#===================
num_guesses = 0
current_guess = -1
value = None
name = None
pwm_buzzer = None
pwm_LED = None
#===================


# Print the game banner
def welcome():
    #os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    #=================
    global value
    global num_guesses
    #=================
    end_of_game = False
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
	#==================
        num_guesses = 0
	#==================
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    count = count[0]
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    #print(raw_data)
    for x in range(3):
        print(str(x) + " - " + raw_data[x][0] + " took " + str(raw_data[x][1]) + " guesses")
    pass


# Setup Pins
def setup():
    # Setup board mode=================================================================================
    global pwm_LED
    global pwm_buzzer
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    for x in range(3):
        GPIO.setup(LED_value[x], GPIO.OUT)
        GPIO.output(LED_value[x], GPIO.LOW)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #print("1")
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    # Setup PWM channels
    #print("2")
    pwm_buzzer = GPIO.PWM(buzzer, 0.1)
    pwm_LED = GPIO.PWM(LED_accuracy, 1000)
    pwm_LED.start(0)
    #print("3")
    pwm_buzzer.start(0)
    #pwm_buzzer.start(50)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, edge=GPIO.RISING, callback=btn_increase_pressed, bouncetime=300)
    GPIO.add_event_detect(btn_submit, edge=GPIO.FALLING, callback=btn_guess_pressed, bouncetime=300)
    #print("4")
    #==================================================================================================
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_block(0,1)
    print(score_count)
    # Get the scores
    scores = eeprom.read_block(0,13)[1:]
    # convert the codes back to ascii
    temp = []
    for s in range(3):
        name = chr(scores[s*4]) + chr(scores[s*4+1]) + chr(scores[s*4+2])
        temp.append([name,scores[s*4+3]])
    scores = temp
    print(scores)
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global name
    global num_guesses
    global end_of_game
    # fetch scores
    count,scores  = fetch_scores()
    count = count[0]
    print(count)
    # include new score
    scores.append([name,num_guesses])
    # sort
    scores.sort(key=lambda x: x[1])
    # update total amount of scores
    count += 1
    # write new scores
    data_to_write = [count]
    if count > 3:
        scores = scores[:3]
    else:
        scores = scores[1:]
    print(scores)
    for s in scores:
        for letter in s[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(s[1])
    print(data_to_write)
    eeprom.write_block(0,data_to_write)
    end_of_game = True
    GPIO.remove_event_detect(btn_increase)
    GPIO.remove_event_detect(btn_submit)
    GPIO.cleanup()
    time.sleep(0.5)
    setup()
    menu()
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess,
    # or just pull the value off the LEDs when a user makes a guess
    if value == None:
        print("No button actions until game begins")
    else:
        print("btn increase")
        global current_guess
        current_guess = 0 if current_guess == 7 else current_guess + 1
        LED1 = [1,3,5,7]
        LED2 = [2,3,6,7]

        if current_guess in LED1:
            GPIO.output(LED_value[0], GPIO.HIGH)
        else:
            GPIO.output(LED_value[0], GPIO.LOW)
        if current_guess in LED2:
            GPIO.output(LED_value[1], GPIO.HIGH)
        else:
            GPIO.output(LED_value[1], GPIO.LOW)
        if current_guess > 3:
            GPIO.output(LED_value[2], GPIO.HIGH)
        else:
            GPIO.output(LED_value[2], GPIO.LOW)
        pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global value
    global end_of_game
    if value == None:
        print("No action")
    else:
        print("btn guess")
        start = time.time()
        while GPIO.input(btn_submit) == GPIO.LOW:
            pass
        length = time.time() - start
        if length > 2:
            pwm_buzzer.stop()
            pwm_LED.stop()
            for x in range(3):
                GPIO.output(LED_value[x], GPIO.LOW)
            end_of_game = True
            GPIO.remove_event_detect(btn_submit)
            GPIO.remove_event_detect(btn_increase)
            GPIO.cleanup()
            time.sleep(0.5)
            setup()
            menu()
            pass
        else:
            global name
            global current_guess
            global num_guesses

            num_guesses += 1
            diff = abs(value-current_guess)
            if diff != 0:
                accuracy_leds()
                if diff <= 3:
                    trigger_buzzer()
            else:
                pwm_buzzer.stop()
                pwm_LED.stop()
                for x in range(3):
                    GPIO.output(LED_value[x], GPIO.LOW)

                print("Correct! The secret number was " + str(value))
                name = input("Please enter your name for the scoreboard: ")
                #global end_of_game
                #end_of_game = True
                save_scores()
                num_guesses = 0
            pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    global current_guess
    global value
    global pwm_LED

    brightness = current_guess/value*100 if current_guess < value else (8-current_guess)/(8-value)*100
    print(brightness)
    pwm_LED.ChangeDutyCycle(brightness)
    pass

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global current_guess
    global value
    global pwm_buzzer
    print("buzzer")

    frequency = 0
    diff = abs(value - current_guess)

    if diff == 3:
        frequency = 1
    elif diff == 2:
        frequency = 2
    else:
        frequency = 4
    print(frequency)
    pwm_buzzer.ChangeFrequency(frequency)
    pwm_buzzer.ChangeDutyCycle(50)
    pass


if __name__ == "__main__":
    try:
        #eeprom.populate_mock_scores()
        #eeprom.clear(16)
        #print(0)
        #eeprom.populate_mock_scores()
        #print(1)
        #fetch_scores()
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
        eeprom.clear(13)
