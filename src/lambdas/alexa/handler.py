import random
from homophones import homophones

def lambda_handler(event, context):
    if event["request"]["type"] == "LaunchRequest":
        return create_response(
            "Let's play deep but not profound!  Ask me for an example to get a pair of words, or once you think you know the rule, give me an example.")

    intent_type = event['request']['intent']["name"]

    kwargs = event['request']['intent'].get("slots", {})
    kwargs = {k: v['value'] if 'value' in v else None for k, v in kwargs.items()}

    skwargs = event["session"]["attributes"]

    kwargs["session"] = skwargs

    new_session = event["session"]["new"]

    return finish_handle({
                             "VerifyIntent": handle_verify,
                             "ExampleIntent": handle_example
                         }.get(intent_type, error)(**kwargs), not new_session)


def finish_handle(response, continue_session):
    if continue_session:
        response["response"]["shouldEndSession"] = False
        response["response"]["outputSpeech"]["text"] += ". Let's keep playing."

    return response


def error(**kwargs):
    return create_response("This should never happen, you are a bad person")


def handle_example(**kwargs):
    example_type = "helpful" if int(kwargs["session"].get("fail", 0)) > 4 else "confusing"
    k, v = get_example(example_type, kwargs["session"]["example"])
    kwargs["session"]["example"][example_type] = v
    return create_response(k, True, kwargs["session"])


def get_example(example_type, attrib):
    examples = {
        "confusing": {
            0: "deep but not profound",
            1: "green but not red",
            2: "yellow but not purple",
            3: "google but not bing",
            4: "apple but not microsoft",
            5: "assist but not help",
            6: "door but not window",
            7: "floor but not ceiling",
            8: "cessna but not piper",
            9: "college but not university",
            10: "school but not learn",
            11: "book but not read",
            12: "see but not sight",
            13: "alliance but not browncoat",
            14: "messy but not clean",
            15: "annoying but not fun"
        },
        "helpful": {
            1: "spelling but not meaning",
            2: "written but not spoken"
        }
    }
    used = attrib.get(example_type, [])
    try:
        idx = rand_exclude(0, len(examples[example_type]), used)
    except IndexError:
        # grab dictionary words?
        idx = 0
    used.push(idx)
    return (examples[example_type][idx], used)


def handle_verify(deep: str, profound: str, **kwargs):

    if deep.lower() in homophones or profound.lower() in homophones:
        return create_response("I can't help you with homophones, they are ambiguous", True, kwargs["session"])

    deep = is_deep(deep)
    profound = not is_deep(profound)

    if deep and profound:
        kwargs["session"]["fail"] = 0
        kwargs["session"]["success"] = kwargs["session"].get("success", 0) + 1
        return create_response("That sounds right!", True, kwargs["session"])
    # elif(deep and not profound):
    #    return create_response("Profound shouln't be deep bro")
    # elif(not deep and profound):
    #    return create_response("Deep shouldn't be profound bruv")
    else:
        kwargs["session"]["fail"] = kwargs["session"].get("fail", 0) + 1
        return create_response("Not quite", True, kwargs["session"])


def create_response(text, should_end_session=True, session_data_dict={}):
    return {
        "version": "1.0",
        "response": {
            "shouldEndSession": should_end_session,
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            }
        },
        "sessionAttributes": session_data_dict
    }


def is_deep(word):
    prev_char = ''
    for char in word:
        if char == prev_char:
            return True
        prev_char = char
    return False


def rand_exclude(min, max, exclude):
    random.choice(i for i in range(min, max + 1) if i not in exclude)