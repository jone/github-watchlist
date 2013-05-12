
def confirmation_prompt(prompt):
    prompt_text = '%s [Yes/No]' % prompt

    answer = raw_input(prompt_text)
    if answer.lower().strip() in ('yes', 'y'):
        return True
    elif answer.lower().strip() in ('no', 'n'):
        return False
    else:
        print 'Please answer with "yes" or "no"'
        return confirmation_prompt(prompt)
