import spacy

def remove_gendered_pronouns_and_names(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    result = " ".join([
        "" if (
            token.pos_ == "PRON" and token.lemma_ not in ["I", "you"]
        ) or (
            token.ent_type_ == "PERSON"
        ) else token.text for token in doc])

    return result.strip()

input_text = """
In the vibrant city of Rivertown , there lived a college student named Jason Harris . Jason was a senior at Rivertown University , majoring in journalism and aspiring to be a storyteller . He had a keen interest in human experiences and a passion for shedding light on untold stories . One day , while perusing the local newspaper , Jason stumbled upon an article about an elderly woman named Mrs . Eleanor Bennett , who had spent decades working as a librarian in the city . Intrigued by the snippet of her life story , Jason felt compelled to dig deeper and share her tale with the world . After some research , Jason learned that Mrs . Bennett had not only been a dedicated librarian but had also been involved in community initiatives , fostering a love for reading among children and organizing events to bring people together . However , her own life story had largely remained in the shadows . Determined to uncover the full narrative , Jason reached out to Mrs . Bennett and asked for an interview . To his surprise , she welcomed the opportunity to share her story , and soon they sat down for a conversation that would unveil a lifetime of experiences . As Jason delved into Mrs . Bennett 's past , he discovered a woman who had overcome personal challenges , witnessed historical events , and touched the lives of many in Rivertown . Her journey was filled with moments of joy , heartbreak , and resilience , making for a compelling narrative that Jason couldn 't wait to share with his readers . With meticulous attention to detail , Jason crafted a feature article that not only highlighted Mrs . Bennett 's contributions to the community but also captured the essence of her character . The story resonated with readers , and the local newspaper received an overwhelming response . Mrs . Bennett became a beloved figure in Rivertown , celebrated for her dedication and the richness of her life story . The success of the article opened doors for Jason , who found himself on the path to becoming a respected journalist . Inspired by Mrs . Bennett 's story , he continued to seek out and share the untold narratives within his community , becoming a storyteller who bridged the gaps between generations . As graduation day approached , Jason reflected on his college journey . His time at Rivertown University had not only provided him with an education but had also instilled in him the power of storytelling to connect people and inspire change . With a heart full of gratitude and a portfolio filled with impactful stories , Jason ventured into the world , ready to make a difference , one narrative at a time .
"""
output_text = remove_gendered_pronouns_and_names(input_text)
print(output_text)
