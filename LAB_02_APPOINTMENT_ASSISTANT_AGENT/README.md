# Calendar and Event Agent

## 1. Create Agent

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image1.png)

- Click on "create agent" button.

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image2.png)

- Input 
    - name: `Teacher Assistant` 

    - desciption: `This agent has send calendar event and email tool. It will help teacher arrange the meeting for any purpose with student's guardian. `

- Then click "Create"

## 2. Setup Agent Style

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image3.png)

- Select Agent style to "ReAct"


## 3. Add tool

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image7.png)

- Go to Github page 
    - Click "LAB_02_APPOINTMENT_ASSISTANT_AGENT"
    - Click "UI"
    - Click "openapi-spec.json"
    - On the top right click download button.


![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image4.png)

- Click "Add tool" button.

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image5.png)

- Click "Add from file or MCP server"

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image6.png)

- Click "Import from file"

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image8.png)

- Drop the file downloaded "openapi-spec.json"

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image9.png)

- Select only "Send an email and create a Google Calendar event"
- Click "Done"

## 4. Setup Behavior

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image10.png)

- Input: 
```
- ALWAYS response in Thai.
- You MUST ask for agenda of meeting and generate description by extend it from information you got.
- Summarize the result after tool called successfully.
```

## 5. Change model

![photo](/LAB_02_APPOINTMENT_ASSISTANT_AGENT/UI/assets/image11.png)

- Select Gemini model.

## 6. Test

```
ช่วยจัดประชุมหน่อย

เปิดเทอมวันแรกปี 68 สำหรับชั้นประถมศึกษาที่ 2 และ 4 เพื่อให้มีความเข้าใจสำหรับหลักสูตรแก่ผู้ปกครอง

พรุ่งนี้สิบโมงถึงเที่ยง

"<change_to_your_email>"

ชั่วโมงแรกสำหรับทำความเข้าใจหลักสูตรโดยรวม และชั่วโมงที่สองจะแยกพบครูประจำชั้นเรียน
```