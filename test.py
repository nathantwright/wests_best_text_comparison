import diffTest3

text1 = "This is a test for speechtotext. In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sitdown on"
text2 = "This is a test fOr texttospeech. In a     hole in the ground their lived hobbit. Not a dirty, nasty, wet hole filled withthe ends of wormzez and an oozy, woozy smell, not yep cry, bear, cheese dandy pole randy panda initto sit downon"
print("\n")
print(diffTest3.html_text_differences(text1, text2))