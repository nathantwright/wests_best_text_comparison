import difflib
import string
import itertools

def _parse_word(word):
    """Returns the argument in all lower case, with punctuation stripped from the beginning and end."""
    parsed_word = word.lower()
    if parsed_word[0] in string.punctuation:
        parsed_word = parsed_word[1:]
    if parsed_word[-1] in string.punctuation:
        parsed_word = parsed_word[:-1]
    return parsed_word

def _compare_short(output_array, argument_array):
    """Function to markup incorrect sequences of words"""
    added_elements = []
    removed_elements = []
    for item in argument_array:
        if item[0] == "+":
            added_elements.append(item[2:])
        else:
            removed_elements.append(item[2:])
    
    if len(added_elements) == 0 and len(removed_elements) != 0:
        for item in removed_elements:
            output_array.append('<span class="removed-text">'+item+'</span>')
    elif len(removed_elements) == 0 and len(added_elements) != 0:
        for item in added_elements:
            output_array.append('<span class="added-text">'+item+'</span>')
    elif len(removed_elements) == 0 and len(added_elements) == 0:
        pass
    else:
        arrays_map = _words_pairer(removed_elements, added_elements)
        formatted_array = _make_formatted_array(removed_elements, added_elements, arrays_map)
        for pairing in formatted_array:
            output_array.extend(_markup_pairing(pairing))
    return output_array

def _markup_pairing(pairing):
    """Takes a list with 2 items, each is a list of words. Finds the best way to match those lists and returns that way in an unlayered list"""
    # [[rem1, rem2, ...], [add1, add2, ...]]
    rem_combs = []
    for x in range(len(pairing[0])):
        for c in range (len(pairing[0]) - x):
            rem_combs.append([y+c for y in range(x+1)])
    add_combs = []
    for x in range(len(pairing[1])):
        for c in range (len(pairing[1]) - x):
            add_combs.append([y+c for y in range(x+1)])
    mix_combs = []
    for l in rem_combs:
        for m in add_combs:
            mix_combs.append([l, m])
    
    for pair in mix_combs:
        rem_temp = ""
        for x in pair[0]:
            rem_temp += pairing[0][x]
        add_temp = ""
        for x in pair[1]:
            add_temp += pairing[1][x]
        pair.append(score_diffs(rem_temp, add_temp))

    new_mix_combs = []
    for pair in mix_combs:
        if pair[2] < 0.4:
            new_mix_combs.append(pair)

    full_combs = _unique_combinations(new_mix_combs)
    solve = ()
    solve_score = 1000.0
    for potential_comb in full_combs:
        final_score = 0
        used_rems = []
        used_adds = []
        fail = False
        for part in potential_comb:
            final_score += part[2]
            for used in part[0]:
                if used in used_rems:
                    fail = True
                    break
                used_rems.append(used)
            for used in part[1]:
                if used in used_adds:
                    fail = True
                    break
                used_adds.append(used)
        if not fail:
            score = (final_score/len(potential_comb))
            if score <= solve_score:
                solve = potential_comb
                solve_score = score

    output = []
    if solve_score > len(solve):
        for r in pairing[0]:
            output.append('<span class="removed-text">'+r+'</span>')
        for a in pairing[1]:
            output.append('<span class="added-text">'+a+'</span>')
    else:
        for p in solve:
            for c in range(len(p[0])):
                i = p[0][len(p[0])-c-1]
                pairing[0].pop(i)

            new_a = ""
            for c in range(len(p[1])):
                i = p[1][len(p[1])-c-1]
                new_a = pairing[1][i] + " " + new_a
                pairing[1].pop(i)
            new_a = new_a[:-1]
            pairing[1].insert(p[1][0], '<span class="changed-text">'+new_a+'</span>')
        for r in pairing[0]:
            if r[0] != "?":
                output.append('<span class="removed-text">'+r+'</span>')
            else:
                output.append(r)
        for a in pairing[1]:
            if a[0] != "?":
                output.append('<span class="added-text">'+a+'</span>')
            else:
                output.append(a)
    return(output)

def _unique_combinations(s):
    """Takes an iterable s and finds out all of the ways any number of the items of s can be uniquely combined"""
    all_combinations = []
    for r in range(1, len(s) + 1):
        combinations_r = list(itertools.combinations(s, r))
        all_combinations.extend(combinations_r)
    return all_combinations

def score_diffs(word1, word2):
    """Takes 2 words and outputs a similarity score"""
    diff_lib = difflib.Differ()
    differences = diff_lib.compare(word1, word2)

    num_diffs = 0
    for diff in differences:
        if diff[0] == "+" or diff[0] == "-":
            num_diffs += 1
    #print(num_diffs, "/", (len(word1) + len(word2)))
    return (num_diffs / (len(word1) + len(word2)))

def _make_formatted_array(removed_elements, added_elements, arrays_map):
    """Produces a formatted array, combining the first 2 args using the 3rd, 
    e.g. [ [[r1],[a1]], [[r2, r3], [a2]], [[r4], [a3, a4, a5]] ]"""
    output = []
    for c in range(len(arrays_map)):
        mapping = arrays_map[c]
        output.append([[],[]])
        output[c][0] = removed_elements[:(mapping[0])]
        output[c][1] = added_elements[:(mapping[1])]
        removed_elements = removed_elements[(mapping[0]):]
        added_elements = added_elements[(mapping[1]):]
    return output

def html_text_differences(reference_text, transcript_text):
    """Returns the differences between text inputs as a marked up html string"""
    # Create lists of words
    reference_text_words = reference_text.split(" ")
    transcript_text_words = transcript_text.split(" ")
    reference_text_words = [i for i in reference_text_words if i != ""]
    transcript_text_words = [i for i in transcript_text_words if i != ""]

    # Parse the lists to avoid punctuation and case mistakes being picked up
    parsed_reference_words = list(map(_parse_word, reference_text_words))
    parsed_transcript_words = list(map(_parse_word, transcript_text_words))

    # Perform comparison using difflib
    diff_lib = difflib.Differ()
    differences = diff_lib.compare(parsed_reference_words, parsed_transcript_words)
    
    # Turn the result of the comparison into an array, removing the lines starting with "?"
    diff_array = []
    for word in differences:
        if word[0] != "?":
            diff_array.append(str(word))
    
    output_array = []
    argument_array = []
    for line in diff_array:
        if line[0] == " ":
            if len(argument_array) > 0:
                output_array = _compare_short(output_array, argument_array)
                argument_array = []
            output_array.append(line[2:])
        else:
            argument_array.append(line)
    if len(argument_array) > 0:
        output_array = _compare_short(output_array, argument_array)

    return " ".join(output_array)

def _words_pairer(removed_elements, added_elements):
    """Attempts to group removed words with their corresponding added words"""
    str1 = " ".join(removed_elements)
    str2 = " ".join(added_elements)

    diff_lib = difflib.Differ()
    differences = diff_lib.compare(str1, str2)

    ctr = 0
    output = [""]
    for d in differences:
        if d[0] == " " and d[2] == " ":
            output.append("")
            ctr += 1
        else:
            if d[0] == " ":
                output[ctr] += "=" + d[2]
            else:
                output[ctr] += d[0] + d[2]

    output_map = []
    for c in range(len(output)):
        weird_word = output[c]
        output_map.append([1, 1]) # [Number of words from removed_elements, Number of words from added_elements]
        for i in range(0, len(weird_word), 2):
            if weird_word[i]+weird_word[i+1] == "- ":
                output_map[c][0] += 1
            elif weird_word[i]+weird_word[i+1] == "+ ":
                output_map[c][1] += 1
    
    return output_map

# If I were to improve this, I would attempt to get it to markup the text in the same places but with the original casing and punctuation