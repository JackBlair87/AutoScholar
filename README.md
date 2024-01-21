## Inspiration

I have been wanting to learn about cognitive architectures in AI systems for a long time. But, as it turns out, delving into such a complex research topic on a whim at 3 AM in the morning is not sustainable. To combat this, I've been trying to read summaries of newer research papers every day. 

## What it does

That's why I build AutoScholar- A simple AI Agent to search the internet every day for research papers relevant to my area of interest (in this case, cognitive architectures!). The agent beautifully summarizes each paper it finds- with an emphasis on impact of the paper- and intelligently sends papers to me it thinks I would find interesting. 

## How I built it

As an AI Agent Engineer, I have a lot of experience building with generative AI tools such as GPT-4 and LangChain. To build this particular workflow, I used an automated scheduling tool called n8n to start a LangChain thread that has access to an arXiv tool, allowing it to search through research papers. That system layered with additional summarization prompts and repetition checking allowed me to send relevant papers every few hours (or however often I want). To display the results of the agent to the user, I used Spooky AI's Human API app, which allowed me to send the notifications. 

## Challenges we ran into

Devops. I hate devops. AI infrastructure is still in a very fragile state with has been annoying. 

## Accomplishments that we're proud of

From what I can tell this is the first consumer facing autonomous research assistant that is completely asynchronous! It will be very interesting to see how helpful this becomes over the next few weeks and I'll see if I can expand it to my friends' interests too!

## What's next for AutoScholar - AI Summarized Research Papers Daily!

We'll see :)
