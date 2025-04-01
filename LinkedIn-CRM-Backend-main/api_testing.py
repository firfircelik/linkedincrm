import openai
import random
import time

# Set up your OpenAI API credentials
openai.api_key = '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'  # WARNING: Don't expose your API key in public forums or scripts. Always keep it private.

def get_intro_message(name, experience, myname):

    model_engine = "text-davinci-003"
    
    # Define your prompts
    prompt_1 = f"""Write LinkedIn introduction message that seems realistic and in profesional english to {name} with the experience : {experience}. The message should include a hypothetical position that would be a career progression from this person's experience as an example of a typical progression if they are a VP then you would offer them a CEO role if they are a manager then they would be the director and be intuitive to figure out the chain of command. You should mention the job title based on this person experience and not the fact that it would be a progression or anything that would allude to it being a progression. please write it in the manner that is a message from an independent recruiter called {myname.split(" ")[0]} to a potential candidate, but no need to introduce yourself. please ask for a contact number to reach them on. Make it humanized Summarise their experience without mentioning years and pick the skills from their experience and explain how it would apply to the role on offer Don't reference all of their work or list every job title that they've had, just interpret it and say how it's relevant to the job on offer Use phrases like "from what i've gathered by your profile..." start with saying something like "im just working with a client" Don't be too enthusiastic or cringe. You should only say something like how their skills will apply to the role or similar too Also write in a way that you think this person is most likely to respond to Take into consideration if they are a company owner, try a different approach that isn’t a direct job offer. shorten things you're trying to say to sound more professional. Keep it 66 words don't be over complimentary and use something specific that stands out ask if they would like to find out more and if they are to etc """
    prompt_2 = f"""The following is to provide examples of dialogue between a recruiter and a candidate in order to train members of staff. I will provide an example of a candidate's name and their experience. The message should give a quick brief of a role that they are working on with a client. The role should be perceived as a potential step up from their current position but not directly mention that> Keep it 100 words or less Just use their first name This is in the format of a LinkedIn outreach message Mention something from their experience and do not mention their number of years of experience and why it would be useful for the position on offer The recruiter is called {myname.split(" ")[0]} use expressions like I'm just working with a client and I came across your profile Don't come across as cringe or overly enthusiastic and come across as Don't introduce yourself and end with {myname} Please put it in the correct format Start with Hey "first name". Candidate Name: {name} and his experience is {experience}. Please use 7Cs of communication and concenterate more on conciseness """
    prompt_3 = f"""The targeted LinkedIn profile name is {name} with this experience {experience}. The following information added is to help learn from examples of dialogue between a recruiter and a candidate as a scenario in order to train members of staff. I will provide an example of a candidate's name and their experience and other nuances from their profile. 
                    With this, can you give an introductory statement that is written in a way to attract the potential candidate to engage in conversation. This intro is written by {myname}.
                    It should give a concise summary of a role that would seem logical and progressive and mention key factors that they would see as a milestone or significant and be proud of. Analyse any psychometric clues taken from their profile to help understand what this person would likely want in whatever stage in their career. The role should be perceived as a potential step up from their current position but not directly mention it.
                    Mention the job title on offer but don’t undermine their current role by alluding to it being a step up. 
                    Abbreviate job titles into CEO, CCO etc not the full written title. 
                    Keep it 70-100 words and just use their first name like Hey “first name” 
                    This is in the format of a LinkedIn outreach message
                    The recruiter is called {myname}. use expressions like “I'm just working with a client” or “I came across your profile” or “I’ve been looking through” (be innovative here but not cringe or overly complimentary) 
                    Don't come across as cringe or overly enthusiastic but remain complimentary when suited. Pick something detailed to make out like you too the time and gave attention to their profile “ 
                    End with something like 
                    “Best, 
                    {myname}” or something similar 
                    Start with Hey "first name"

                    Below are some examples of the types of introductory messages I’m looking for. 
                    Pay attention to how they are written and the detail in them. 

                    Hey Deniz,   

                    I've been looking at your extensive ERM and BCM expertise at Ooredoo Qatar, especially the ISO 22301 BCMS certification. I'm working with a client seeking a Vice President of Risk Management to drive global risk initiatives. 
                    Your proactive approach and CEO Excellence Award in 2021 caught my eye. 
                    If you’d be open for a discussion, please share a contact number and a suitable time for a call. 

                    Regards, 

                    {myname}

                    Hey Andre, 

                    I stumbled upon your profile while looking for individuals with a unique blend of expertise in both travel marketing and investment migration. 
                    Your work at Sovereign Man, especially around Golden Visas and passive income visas, is genuinely remarkable. I'm currently working with a client seeking a Senior Marketing Director, particularly someone with your deep industry insights. 
                    Would you be available for a brief chat? If so, please share a number to contact you on. 

                    Thanks, 

                    {myname}

                    Hey Ashwin, 

                    Hope you've had productive discussions at the ASEAN Wind Energy 2023 Conference. 
                    Your insights in sustainable infrastructure, especially in emerging markets, caught my attention. Your 2-year tenure with BlueOrchard Finance and your expertise in closing the SDG funding gap is quite commendable. I'm working with a client who's looking for a Global Infrastructure Investment Director role. Given your trajectory, this might align with your aspirations. Would you be open for a discussion at all? If so, whats the best number to reach you on? 

                    Best, 

                    {myname} 

                    Hey Charles, 
                    I came across your profile and was particularly drawn to your extensive experience with Greencells Group and your previous focus on renewable energy contracts at Lighthouse Law. I'm just working with a client who's seeking someone with your unique blend of skills and background for a pivotal legal role.
                    Let me know if you’d be open for a discussion, and if so what would be the best number to reach you on?

                    Thanks, 
                    """
    
    # Randomly select a prompt
    #prompt = random.choice([prompt_1, prompt_2])

    
    # Get response from OpenAI API
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt_3,
        max_tokens=8000,
        n=1,
        stop=None,
        temperature=0.8,
    )
    response = completion.choices[0].text.strip()
    
    # Make replacements as necessary
    response = response.replace("[Name]", name).replace("[name]", name).replace("[Your Name]", myname).replace("[Your name]", myname).replace("[your name]", myname)
    
    return response


names = ["Peter", "Declan", "Paul"]
experiences = ["Managing Director at PMCE", "Managing Director Kilmartin Construction Ltd Mar 1984 - Present · 39 yrs 8 mos", "Managing Director at Pat O'Gorman & Associates"]
for n, name in enumerate(names):
   print(get_intro_message(name, experiences[n], "Sofia Martinez"))

def get_follow_up(name, myname, conversation):
    model_engine = "text-davinci-003"
    
   
    # Randomly select a prompt
    prompt = f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}"""
    
    # Get response from OpenAI API
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.8,
    )
    response = completion.choices[0].text.strip()
    response = response.replace("[Name]", name).replace("[name]", name).replace("[Your Name]", myname).replace("[Your name]", myname).replace("[your name]", myname)

    print(response)
    time.sleep(5)
    return response
