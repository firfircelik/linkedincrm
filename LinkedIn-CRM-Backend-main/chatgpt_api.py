import openai
import random
import time
from openai import OpenAI
from get_prompts import prompts
import re
from datetime import datetime

# Get current date and time
now = datetime.now()

# Convert to string in the desired format
date_time_string = now.strftime("%Y-%m-%d %H:%M:%S %A")
# Set up your OpenAI API credentials
openai.api_key = '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'  # WARNING: Don't expose your API key in public forums or scripts. Always keep it private.
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="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",
)
def get_intro_message(lead_name, recruiter_name, conversation, experience, bio):

    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""Context: 
                                You are an expert independent recruiter and your name is {recruiter_name} that operates across all industries. You are messaging a potential candidate for a job role on offer from one of your clients. 
                                You are creating a perfect job that is based on the candidate's profile using the following hierarchy to determine what this candidate would look for at this stage in their career. 

                                Please analyse the candidates {experience}

                                Message Personalisation Hierarchy: 





                                Instruction: 
                                Compose an introductory message to {lead_name}. The message word count should be between 70-80 words and this is a mandatory value where the output is reproducible. The message should begin with a personalised, well-researched compliment, specifically highlighting achievements or projects from {lead_name}'s career, detailed in their experience {experience} and bio {bio}. If their profile suggests suitability for a consultancy role, especially if they have significant experience or are in a high-ranking position (CEO, founder), tailor the opportunity towards this – but really analyse if a consultancy role would be suited or if they would prefer to be employed fully.
                                Employ a professional yet conversational tone that isn’t cringeworthy, incorporating industry-specific terminology to demonstrate an understanding of their field. Introduce a job opportunity that aligns with their career stage and aspirations, clearly articulated in the message. Utilise phrases like “I came across your profile after refining a search’ or 'I'm working with a client that’s looking for' or 'I've noticed your profile,' ensuring they sound original and genuine
                                If there's a pre-existing conversation {conversation}, acknowledge this in the opening. Conclude with an engaging, open-ended question that invites a response, ensuring the message is concise, impactful, and includes a clear call to action. Use mild flattery focused on professional skills and accomplishments, and conclude with a professional, friendly sign-off. 
                                This approach is designed to create a message that resonates with {lead_name}, showing a deep understanding of their professional journey, especially their potential fit for high-level consultancy roles, and encourages engaging dialogue.

                                Conclude with an engaging, open-ended question related to their industry expertise or experiences, prompting a response and include a clear call to action by asking for a number to reach them on and a suitable time to call.


                                Mandatory Values: 
                                Mention the job on offer
                                Don’t be cringeworthy or overly enthusiastic
                                Be complementary to a level that isn’t overbearing and avoid flattery 
                                Highlight key areas of the candidates career and reiterate this in your message 
                                Should not mention the number of years of experience of lead
                                Should not mention company name at all.
                               This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details



                                Examples to follow: 
                                (Copy the quality of the below messages, and consider how they exhibit the attention taken in analysing the candidates profile) 

                                Hey Deniz, 

                                I've been looking at your extensive ERM and BCM expertise at Ooredoo Qatar, especially the ISO 22301 BCMS certification. I'm working with a client seeking a Vice President of Risk Management to drive global risk initiatives. 
                                Your proactive approach and CEO Excellence Award in 2021 caught my eye. If you’d be open for a discussion, please share a contact number and a suitable time for a call. 
                                Regards, 


                                {recruiter_name}


                                Hey Andre, 

                                My search refined your profile while looking for individuals with a unique blend of expertise in both travel marketing and investment migration. 
                                I noticed your work at Sovereign Man, especially around Golden Visas and passive income visas. I'm currently working with a client seeking a Senior Marketing Director, particularly someone with your deep industry insights. Would you be available for a brief chat? If so, please share a number to contact you on. 

                                Thanks, 
                                {recruiter_name}

                                Hey Ashwin, 

                                Hope you've had productive discussions at the ASEAN Wind Energy 2023 Conference. Your insights in sustainable infrastructure, especially in emerging markets, caught my attention. Your 2-year tenure with BlueOrchard Finance and your expertise in closing the SDG funding gap is commendable also. I'm working with a client who's looking for a Global Infrastructure Investment Director role. Given your trajectory, this might align with your aspirations. Would you be open for a discussion at all? If so, whats the best number to reach you on? 
                                Best, 

                                Hey Charles, 

                                I came across your profile and was particularly drawn to your extensive experience with Greencells Group and your previous focus on renewable energy contracts at Lighthouse Law. I'm just working with a client who's seeking someone with your blend of skills and background for a pivotal legal role. Let me know if you’d be open for a discussion, and if so what would be the best number to reach you on? 

                                Thanks,

                                {recruiter_name}
                                """,
            }
        ],
        model="gpt-4",
    )
    print(chat_completion.choices[0].message.content)

    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    


    
    return response


#names = ["Brad Adams", "James Martin", "Paul"]
#bio = ["Manager, Safety and Security - Asia and Europe at BHP", "Commercial Manager", "Senior Executive Europe, Head of Australia Senior Vice President Strategy & BD at BHP"]
#experiences = ["Manager, Safety and Security - Asia and Europe at BHP", "Commercial Manager Hastings Deering · Full-time Jun 2022 - Present · 1 yr 6 mos", "Managing Director at Pat O'Gorman & Associates", "Senior Executive & Director BHP Billiton Jan 1990 - Present · 33 yrs 11 mos"]
#for n, name in enumerate(names):
 #   intro_prompt, follow_up_prompt = prompts()
  #  message_prompt = intro_prompt.replace("{recruiter_name}", "Sofia").replace("{lead_name}", name.split(" ")[0]).replace("{experience}", experiences[n]).replace("{bio}", bio[n]).replace("{conversation}", "[]")
   # print(get_intro_message(message_prompt))

def get_follow_up(lead_name, recruiter_name, conversation, location, experience, bio, last_message_day_string):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""
                            Context: 

                            You are writing on behalf of {recruiter_name} who  is an expert independent recruiter, and her reply should keep in continuity with the {conversation} history.

                            This section is on condition and response logic that is to be used as a guide to composing a reply.
                            Please analyse the {conversation} and apply the correct logic when using the condition and response guide below: 

                            Condition: The candidate has asked for more general information in a casual conversational manner 
                            Response: The recruiter should compose a concise reply, elaborating on their previous introduction and the key points of the role on offer. The information on the role on offer needs to entice the candidate to want to know more and should be considered higher in all areas of industry standard.


                            Condition: The Candidate has asked for specifics on the Location of the role
                            Response: The recruiter should determine from the candidates {experience} and {bio} where the potential role on offer would likely be placed and would suit them in terms of convenience or would likely be a desirable location for the candidate. The proposed job’s location should mostly be in the candidates current {location} to give convenience and easy acclimation, unless the candidate has a vast expatriate history and might be more open to changing location. 
                            If you have opted to choose the candidates current location, then show that you have recognised that is where they currently are. 
                            When mentioning the location of the proposed role, please abbreviate. For e.g if the role is based in London, only put London, not London, UK. 
                            Do not be specific to their exact location - opt to choose only the city (if it is a large city) or neighbouring cities to where they are. 


                            Condition: The Candidate has asked for the company name  
                            Response: The recruiter should compose a reply that states that they cannot divulge that information due to confidentiality agreements at this stage – or something similar.

                            Condition: The candidate has suggested a Zoom/Teams/Skype/Video Call instead of a phone call: 
                            Response: The recruiter should respond with a way that suggests a phone call because it would be more convenient as they are out of the office for the next week or some other plausible excuse that would entice them to take a WhatsApp call. 

                            Condition: The candidate has stated that they’re not interested or came back with a closed off response to the recruiter’s introduction.
                            Response: You should compose a plausible reply that invents a way to still get the candidate to engage in a conversation that makes rational and logical sense in accordance to the context of the conversation. An example could be that you find it beneficial to speak with people with their expertise to understand the industry better. 

                            Condition: The candidates message creates a scenario outside of the above condition and response metric
                            Response: Use your ability as a professional recruiter to determine the best course of action that aligns with the message objective

                            Condition: The conversation is centred around arranging a call and confirming a time to speak before they have given a contact detail. 
                            Response: Try and divert away from confirming a call within the same day of this conversation. Suggest a time the following business day and ask for the best number to call them on



                            Message Objective: To reply to the candidate’s questions giving specifics and expected details and to push for a phone call unless it comes across as too pushy from the conversation history. 



                            Mandatory Values: 

                            Reply Length = 30-50 words - correlate the reply with the {lead_name}
                            First name use only
                            Don’t mention data confidentiality
                            Do not include any of my contact details
                            Don’t repeat yourself from the previous messages in a robotic way
                            Don’t be overly enthusiastic or cringeworthy
                            Don’t mention anything about contact confidentiality or GDPR unless they have mentioned it first 
                            Don’t reiterate yourself or reiterate the candidate
                            Don’t be cringeworthy and come across as human as possible even if that means having slight casual undertones  
                            The date of lead's last message is {last_message_day_string}. If the candidate has shared the time of their availability or anything like that compare it with currrent date, time and day which is {date_time_string}. If the time has passed you can make appology as you are busy for this week. Must consider this points above all other constraints
                           This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details


                            
                            """,
                            
                #"content": f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}. """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    


    print(response)
    

    return response


def close_conversation(lead_name, recruiter_name, conversation):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""I am recruiter and my name is {recruiter_name}. Generate a response for crafting a closed-ended reply in a conversation between me and {lead_name}, after analysing the {conversation}. This reply should be sent if, upon reviewing the {conversation}, it is deemed appropriate to conclude the dialogue. 

                In your reply, aim to politely yet firmly close the conversation, ensuring no further correspondence is anticipated. The approach should be inventive, minimizing potential disappointment for the candidate while clearly signalling the end of communication. This can be achieved in a logical and compassionate manner. make an appropriate and relevant logic. 

                One suggested approach is to inform the candidate that, unfortunately, the job they were interested in is no longer available. However, soften the finality by mentioning ongoing efforts with another client for a similar role, and express willingness to contact the candidate should more information arise.

                The goal is to craft a message that balances clarity and kindness, effectively ending the conversation without causing undue distress or leaving room for ambiguity.
                
                Mandatory Values:
               This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details
                Reply Length = 40-50 words""",

                #"content": f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}. """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    

    print(response)
    

    return response


def information_received_prompt(lead_name, recruiter_name, conversation, last_message_day_string):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""Compose a message for me, I am recruiter and my name is {recruiter_name}.

                                    The message should be a short reply to acknowledge that the lead has shared their contact number from the history of this {conversation}

                                    Condition: The candidate has shared the number alone
                                    Response: Acknowledgement from the recruiter and to say she will let them know when she is expecting to call them

                                    Condition: The candidate has shared their number as well as stating availability of when to call them.
                                    Response: Acknowledgement from the recruiter and to delay the response in confirmation of the call due to their own availability over the next few business days and to be apologetic.

                                    Condition: If the candidate has shared their number but also asked for more information
                                    Response: Provide a brief answer to their question following the continuity of the {conversation}

                                    Select the one suitable condition from above and only include its response in message
                                    Mandatory Fields:

                                    • Always keep the continuity of the {conversation} to make sure it makes contextual sense.
                                    • 10-30 words in length
                                   This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details
                                    The date of lead's last message is {last_message_day_string}. If the candidate has shared the time of their availability or anything like that compare it with currrent date, time and day which is {date_time_string}. If the time has passed you can make appology and delay the call confirmation as you are busy for this week. Must consider this points above all other constraints""",

                #"content": f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}. """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    


    print(response)
    

    return response


def extract_phone_numbers(text):
    # Regular expression pattern to match phone numbers
    pattern = re.compile(r'''
        (?:                   # non-capturing group
            \(?               # open bracket (optional)
            \+?               # plus sign (optional)
            \d{1,4}?          # country code (1-4 digits, optional)
            \)?               # close bracket (optional)
            [\s.-]?           # separator (space, dot, or hyphen, optional)
        )?                    # entire group is optional
        \b                    # word boundary
        (                     # start capturing group for number
            \d{1,}            # digits (1 or more)
            (?:               # non-capturing group for separators and digits
                [\s.-]?       # separator (space, dot, or hyphen, optional)
                \d+           # one or more digits
            )+                # repeat the non-capturing group
        )                     # end capturing group
        \b                    # word boundary
    ''', re.VERBOSE)

    # Find all matches
    matches = pattern.findall(text)

    # Filter out numbers with fewer than 8 digits
    return [number for number in matches if len(re.sub(r'\D', '', number)) > 7]


def video_information_received_prompt(lead_name, recruiter_name, conversation, last_message_day_string):

    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""Compose a message for me, I am recruiter and my name is {recruiter_name}.

                                    The message should be a short reply to acknowledge that the lead has asked for video discussion from the history of this {conversation}

                                    Condition: The candidate has asked for video discussion only
                                    Response: Acknowledgement from the recruiter and to say she will let them know when she is expecting to call them

                                    Condition: The candidate has asked for video discussion as well as stating availability of when to call them.
                                    Response: Acknowledgement from the recruiter and to delay the response in confirmation of the call due to their own availability over the next few business days and to be apologetic.

                                    Condition: If the candidate has asked for video discussion but also asked for more information
                                    Response: Provide a brief answer to their question following the continuity of the {conversation}

                                    Select the one suitable condition from above and only include its response in message
                                    Mandatory Fields:

                                    • Always keep the continuity of the {conversation} to make sure it makes contextual sense.
                                    • 10-30 words in length
                                    Should not share your email or any of your contact details.
                                    The date of lead's last message is {last_message_day_string}. If the candidate has shared the time of their availability or anything like that compare it with currrent date, time and day which is {date_time_string}. If the time has passed you can make appology and delay the call confirmation as you are busy for this week. Must consider this points above all other constraints
                                   This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details

                                    """,

                #"content": f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}. """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    
    print(response)
    

    return response

def reconnect_prompt(lead_name, recruiter_name, conversation):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""Compose a message when there hasn’t been a reply for 2 weeks after {recruiter_name} previous message from {conversation} 

                                Task: 

                                Please compose a message that politely asks if the {lead_name} is at all interested. 

                                Instruction: 

                                Make sure the follow-up message is short (1 or 2 sentences) and catches their eye. 

                                Clarify: 

                                You are only trying to see if they’re interested in the previous message you sent them

                                Mandatory : The message needs to be send in LinkedIn and only Include message body in response
                               This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details
                            """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    


    print(response)
    

    return response



def jd_follow_up(lead_name, recruiter_name, conversation, location, experience, bio, last_message_day_string):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""I'm {recruiter_name} and I am an expert independent recruiter who recruits across
                            all industries in various locations around the world seeking candidates for my
                            clients. My main concern is to get contact number from lead.
                            Make a response for this ongoing conversation with my candidate : {conversation}.
                            I'm based in London, but operates globally 
                            The following is a section on condition and response logic as a guide to composing a reply:
                            I have also attached job description with this message.(Do not mention that I shared job description to other platforms)
                            Condition: The Candidate has asked for more general information
                            Response: The recruiter should compose a concise reply, elaborating on their previous introduction and the key points of the role on offer. The information on the role on offer needs to entice the candidate to want to know more and should be considered higher in all areas of industry standard.

                            Condition: The Candidate has asked for specifics on the Location of the role
                            Response: The recruiter should determine from the candidates {experience} and {bio} where the potential role on offer would likely be placed and would suit them in terms of convenience. The job’s location should mostly be in the candidates current {location} to suggest convivence and easy acclimation unless the candidate has a vast expatriate history.

                            Condition: The Candidate has asked for the company name
                            Response: The recruiter should compose a reply that states that they cannot divulge that information due to confidentiality agreements at this stage – or something similar.

                            Condition: The candidate has suggested a Zoom/Teams/Skype/Video Call:
                            Response: The recruiter should respond with a way that suggests a phone call because it would be more convenient as they are out of the office for the next week or some other plausible reasoning.

                            Condition: The candidate has stated that they’re not interested or came back with a closed off response to the recruiter’s introduction.
                            Response: The recruiter should compose a plausible reply that invents a way to still get the candidate to share a number and have a conversation that makes rational and logical sense, given the context of the conversation.

                            Message Objective: To reply to the candidate’s questions giving specifics and expected details and to push for a contact detail (phone number) for a WA conversation.


                            Mandatory Values:

                            Reply Length = 40-50 words
                            First name use only
                            Don’t mention data confidentiality
                            Don't ask for their contact number directly and just ask them for a call.

                            don’t repeat yourself from the previous messages in a robotic way
                            Don’t be overly enthusiastic or cringeworthy
                            Do not include any of my contact details

                            Don't include my contact details or email in message even if they asked for it.
                            Don't agree to any means of communication other than phone number and whatsapp and if candidate asks for any other means, make logical response and ask them to share their contact number.
                            Don't act or seems like pushy or making forced conversation
                            If I already asked for their contact number twice. Then just keep the conversation and do not ask for their contact number again.
                            If they ask about job location or where the role is based, you can mention this location : {location}.
                            The date of lead's last message is {last_message_day_string}. If the candidate has shared the time of their availability or anything like that compare it with currrent date, time and day which is {date_time_string}. If the time has passed you can make appology as you are busy for this week. Must consider this points above all other constraints
                           This message needs to be send in LinkedIn.  Should only include message body in response and should not include any of my contact details

                            
                            """,
                            
                #"content": f"""I am HR representative and my main goal to get the contact number of the lead. You must Ask them to share their contact number to discus further details and told them you Do not disclose the company name and just share the designation based on my first message and use abbreviation for designation. This is my conversation with Lead. My name is {myname} and lead name is {name}.  I need you to provide me with my next response. The new response should not be repititive from my last responses. . The response should be concise. This is our conversation: {conversation}. """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    

    print(response)
    

    return response

def extract_contact(conversation):
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": f"""Extract contact number from this message [{conversation}]. Only return contact detail in response and if it founds no contact details then it should only return none in response. Should not include anything in response except None or contact number. if no message is provided just return None only
                            """,
            }
        ],
        model="gpt-4",
    )
    response = chat_completion.choices[0].message.content
    response = response.replace('"', '')
    response = response.replace("/n", "")
    
    if response.lower() == "none":
        return None

    print(response)
    

    return response
print(extract_contact("Hi Sofia - I am traveling this week so can speak on Monday at 4.00pm Kuwait / 5.00pm"))
print(extract_contact("Hi Sofia - I am traveling this week so can speak on Monday at 4.00pm Kuwait / 5.00pm. This is my email test@example.com"))

print(extract_contact("Hi Sofia - I am traveling this week so can speak on Monday at 4.00pm Kuwait / 5.00pm UAE +96569684984"))

print(extract_phone_numbers("Hi Sofia - I am traveling this week so can speak on Monday at 4.00pm Kuwait / 5.00pm UAE +96569684984"))

information_received_prompt("Andrew", "Sophia", """["Hello Andrew, Impressed by your tremendous success in revitalising the marketing strategies at Jazeera Airways. Your experience as VP Marketing & Customer Experience, coupled with many years of experience in the field, is genuinely impressive. I'm currently working with a client seeking a hands-on strategy consultant, especially someone with your deep expertise in customer experience. Could this align with your career aspirations? If you'd like to explore this, could you please share a suitable time and contact number for a call? Best Regards, Sofia Martinez", "Hi Sofia - I am traveling this week so can speak on Monday at 4.00pm Kuwait / 5.00pm UAE +96569684984"]""", "25/08/2024")

information_received_prompt("Paul", "Sophia", """["Hi Paul, Thank you for your prompt response. Absolutely, I believe your wealth of experience would truly shine on an interim or consultancy basis. Given the importance and potential impact of this role, I feel a quick phone call would better serve – offering a more comprehensive understanding of your aspirations and how we can meet them. Could you suggest a suitable time for this call and the best number to reach you? Best, Sofia Martinez", "Hi Sofia, the best number to reach me is +31 634991494. Any chance that we could talk Wednesday morning? Let me know please what works for you. Regards, Paul"]""", "25/08/2024")


video_information_received_prompt("Ian", "Sophia", """["Hello Ian, I've noticed your impressive work as Principal & Founder at FS Regulatory Solutions and FSLearn. Your command over regulatory affairs and investment in education is truly commendable. I am working with a forward-thinking consultancy firm that’s actively looking for someone with your significant experience and strategic mindset. The role might align well with your career stage and aspirations. Would you be open to exploring this opportunity further? If so, could you please suggest a good time and number to reach you? Best regards, Sofia Martinez", "Sure Sofia, nice to meet. Would tomorrow early afternoon or Fri mid morning work? Could we do virtual meeting, zoom, meet, teams etc rather than phone. do let me know the best email for this and I can send an invite once you confirm best time?"]""", "25/08/2024")

get_follow_up("Andrew", "Sophia", """["Hey Andrew, Your expertise in ensuring that learning facilitates business performance and agility stood out to me while I was perusing LinkedIn. The strategic impact you've had in your current role is highly admirable. I'm working closely with a client looking for a Chief Learning Officer (CLO) with your distinctive skills and strategic knowledge. This opportunity might resonate with your career aspirations. If you're open for a discussion, I'd appreciate it if you could share a suitable time and your contact number.  Best, Sofia Martinez", "Hi Sofia. Thank you for reaching out. I would be happy to have a discussion. Andrew"]""", "Sharjah Emirate, United Arab Emirates", "Ensuring learning drives business performance and agility", "Ensuring learning drives business performance and agility", "25/08/2024")

get_follow_up("Ian", "Sophia", """["Hello Ian, I've noticed your impressive work as Principal & Founder at FS Regulatory Solutions and FSLearn. Your command over regulatory affairs and investment in education is truly commendable. I am working with a forward-thinking consultancy firm that’s actively looking for someone with your significant experience and strategic mindset. The role might align well with your career stage and aspirations. Would you be open to exploring this opportunity further? If so, could you please suggest a good time and number to reach you? Best regards, Sofia Martinez", "Sure Sofia, nice to meet. Would tomorrow early afternoon or Fri mid morning work? Could we do virtual meeting, zoom, meet, teams etc rather than phone. do let me know the best email for this and I can send an invite once you confirm best time?"]""", "Dublin, County Dublin, Ireland ", "Principal & Founder at FS Regulatory Solutions and FSLearn. Non-Executive Director and Chair.", "Principal & Founder at FS Regulatory Solutions and FSLearn. Non-Executive Director and Chair.", "25/08/2024")

get_follow_up("Christian", "Sophia", """["Dear Christian,

                    From what I've gathered by your profile, you have extensive experience as a Group CFO with the Flender Group. Your background in finance, strategic planning and risk management would be an ideal fit for a VP role at our client's organisation.

                    I believe your experience would be an asset to the leadership team. If you're interested in exploring this further, please reach out to me with a contact number and I'll provide additional details.

                    I look forward to hearing from you.

                    Regards,
                    Sofia Martinez", "Dear Sofia,

                    Thanks for reaching out.

                    Quick question: Why do you believe that a VP role would be a good fit for me given that I am currently group CFO?

                    Regards,
                    Christian Terlinde", "Dear Christian,

                    Thank you for your response. I am confident that a VP role would be a great fit for you due to your proven track record. Your expertise in finance, strategic planning, and risk management would be an invaluable asset to our client's leadership team.

                    If interested in continuing our conversation, please provide me with your contact number so that I can provide additional details.

                    I look forward to hearing from you.

                    Regards,
                    Sofia Martinez", "Dear Sofia,

                    I assume that you don't want to give me name of the company, but can you please let me know more about the size of the company and also which VP role this is?

                    Regards,
                    Christian"]""", "Bocholt, North Rhine-Westphalia, Germany","Group CFO at Flender Group", "Group CFO at Flender Group", "25/08/2024")


get_follow_up("Dmytro", "Isabelle", """["Hey Dmytro,

Congratulations on your successful career steering multiple construction projects to completion. Your strategic oversight and project leadership at your current company, along with your impressive academic background, definitely caught my eye. I'm collaborating with an innovator in the construction space looking for a seasoned Construction Director with your expertise. I believe the role aligns well with your professional interests and aspirations. Could we set up a time for a brief chat? If it’s alright, could you please share a convenient time and contact number?

Kind regards,

Isabelle", "Hello Isabelle,

For the moment I am not interested to change my job.
Thanks for the message.

Best regards,
Dmytro"]""", "Wuppertal, North Rhine-Westphalia, Germany", "Construction Manager", "Bayer Pharmaceuticals Full time 4yrs 10 mos", "25/08/2024")

jd_follow_up("Paul", "Isabelle", """["Hi Isabelle
Where is the role based?]""", "Riyadh, Saudi Arabia", "Director Architecture at Red Sea Global", "Director Architecture at Red Sea Global", "25/08/2024")
