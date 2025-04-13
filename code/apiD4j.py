from openai import OpenAI

import os.path
import pickle

model_name = "your_model_name"
api_key = "your_api"
projectOrigin = {
    "Chart": 26,
    "Lang": 65,
    "Math": 106,
    "Mockito": 38,
    "Time": 27,
    "Closure": 176,
}
readFileRootPath = r"changeYourPath\sourceofCodeContext (Defects4J)"
outputFileRootPath = r"changeYourPath\outputName"
repeatArr = [0, 1, 2, 3, 4]


client = OpenAI(
    base_url="your_url",
    api_key=api_key,
    timeout=120
)


def deal():
    for repeatTime in repeatArr:
        for projectName in projectOrigin.keys():
            for versionInt in range(1, projectOrigin[projectName] + 1):
                versionStr = str(versionInt) + "b"

                if projectName == "Closure" and versionStr == "34b":
                    continue

                if projectName == "Closure" and versionStr == "68b":
                    continue

                if projectName == "Closure" and versionStr == "123b":
                    continue

                if projectName == "Closure" and versionStr == "132b":
                    continue

                if projectName == "Closure" and versionStr == "157b":
                    continue

                if projectName == "Closure" and versionStr == "173b":
                    continue

                readFilePath = os.path.join(readFileRootPath, projectName, versionStr, "NLInformation.in")
                if not os.path.exists(readFilePath):
                    continue
                with open(readFilePath, "rb") as file:
                    questions = pickle.load(file)

                outputDirPath = os.path.join(outputFileRootPath, projectName, versionStr)
                if not os.path.exists(outputDirPath):
                    os.makedirs(outputDirPath)

                if repeatTime == 0:
                    outputFilePath = os.path.join(outputDirPath, model_name + ".out")
                    outputTxtPath = os.path.join(outputDirPath, model_name + ".txt")
                else:
                    outputFilePath = os.path.join(outputDirPath, model_name + "_" + str(repeatTime) + ".out")
                    outputTxtPath = os.path.join(outputDirPath, model_name + "_" + str(repeatTime) + ".txt")

                answerList = []
                if os.path.exists(outputFilePath):
                    answerList = pickle.load(open(outputFilePath, "rb"))

                itemindex = -1
                while itemindex < len(questions):

                    itemindex += 1
                    if itemindex >= len(questions):
                        break

                    if len(answerList) > itemindex:
                        continue
                    item = questions[itemindex]

                    print(repeatTime, projectName, versionStr, itemindex, "start", end=" ")
                    if len(item["faultLineContent"]) < 2:
                        print("too short")
                        answerList.append({})
                        continue

                    singleAnswerResult = {}

                    prompt1 = "Please analyze the following code snippet for potential bugs. Return the results in " \
                              "JSON format, consisting of a single JSON object with two fields: " \
                              "'intentOfThisFunction' (describing the intended purpose of the function)," \
                              "and 'faultLocalization' (an array of JSON objects). The 'faultLocalization' array " \
                              "should contain up to five JSON objects, each with three fields: 'lineNumber' (" \
                              "indicating the line number of the suspicious code)," \
                              "'codeContent' (showing the actual code), and 'reason' (explaining why this location is " \
                              "identified as potentially buggy). Note: The codes in the 'faultLocalization' array " \
                              "should be listed in descending order of suspicion."
                    for line in range(len(item["faultLineNumbers"])):
                        prompt1 += str(item["faultLineNumbers"][line]) + ":" + item["faultLineContent"][
                            line].strip() + ""

                    messages = [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt1}
                    ]
                    # res = bot.chat(messages)
                    # res = bot.chat(prompt1)
                    res = client.chat.completions.create(
                        model=model_name,
                        messages=messages
                    )
                    message = {
                        "role": "assistant",
                        "content": res.choices[0].message.content
                    }
                    messages.append(message)

                    singleAnswerResult["answer1"] = res.choices[0].message.content

                    if len(item["errorLogContent"]) > 0:
                        prompt2 = "I have received an error message and a unit test case related to the code snippet " \
                                  "I provided in the first prompt. The error message is: \""

                        testCaseNum = -1
                        for testCaseIndex in range(len(item["testCaseLineNum"])):
                            if len(item["testCaseContent"][testCaseIndex]) > 0 and len(
                                    item["errorLogContent"][testCaseIndex]) > 0:
                                testCaseNum = testCaseIndex
                                print("testCaseNum", testCaseIndex)
                                break

                        if testCaseNum != -1:
                            temp1 = ""
                            for line in range(len(item["errorLogContent"][testCaseNum])):
                                if line > 0 and "---" in item["errorLogContent"][testCaseNum][line]:
                                    break
                                temp1 += item["errorLogContent"][testCaseNum][line].strip() + "\n"

                            prompt2 += temp1[:3000]
                            prompt2 += "\". Additionally, here is the unit test case: \""
                            testCases = ""
                            for line in range(len(item["testCaseLineNum"][testCaseNum])):
                                testCases += str(item["testCaseLineNum"][testCaseNum][line]) + ":" + \
                                             item["testCaseContent"][testCaseNum][line].strip() + "\n"

                            prompt2 += testCases[:1000]
                            prompt2 += "\". Please analyze the parts contained in <code> and </code> from the first prompt, along with the " \
                                       "provided error message and unit test case." \
                                       "Update and return the JSON object consisting of 'intentOfThisFunction' (" \
                                       "describing the intended purpose of the function)," \
                                       "and 'faultLocalization' (an array of JSON objects). The 'faultLocalization' " \
                                       "array should contain up to five JSON objects, each with three fields: " \
                                       "'lineNumber' (indicating the line number of the suspicious code)," \
                                       "'codeContent' (showing the actual code), and 'reason' (explaining why this " \
                                       "location is identified as potentially buggy)." \
                                       "Note: The codes in the 'faultLocalization' array should be listed in " \
                                       "descending order of suspicion, and the analysis should focus exclusively on " \
                                       "the code snippet from the first prompt and not the unit test case."
                            message = {"role": "user", "content": prompt2}
                            messages.append(message)
                            # resLog = bot.chat(messages)
                            # resLog = bot.chat(prompt2)

                            resLog = client.chat.completions.create(
                                model=model_name,
                                messages=messages
                            )

                            singleAnswerResult["answer2"] = resLog.choices[0].message.content

                    answerList.append(singleAnswerResult)

                    with open(outputFilePath, "wb") as file:
                        pickle.dump(answerList, file)
                    with open(outputTxtPath, "w", encoding="utf-8") as file:
                        file.write(str(answerList))


if __name__ == "__main__":
    deal()
