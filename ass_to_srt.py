import io
from datetime import datetime
import re


def parse_text(element) -> str:
        text = ','.join(element['text']).strip().replace("\\N", " ").replace("  ", " ")
        
        if text.startswith('—'):
            text = text.replace("—", "")

        if element['fx']: 
            text = "[" + text + "]"
        else:
            tags = ("\\fn", "\\shad", "\\bord", "\\fade", "\\move", "\\pos", "\\fsc")
            for tag in tags:
                if tag in text:
                    text = "[" + text + "]"
                    break
        
        if element['name'] != '':
            text = "[" + element['name'] + "] " + text

        return re.sub(r'{.*?}', '', text)


def sort_by_time(parsed_lines):
    return parsed_lines['start']


def conc_lines(parsed_lines):
# check if the end time of the current line is greater than the start time of the next line
    new_lines = []
    for i, line in enumerate(parsed_lines):
        start = line['start']
        end = line['end']
        text = line['text']


        for line in parsed_lines:
            if i < len(parsed_lines):
                next_line = parsed_lines[i+1]
                next_start = next_line['start']
                next_end = next_line['end']
                next_text = next_line['text']
                
                if end == next_start and text == next_text:
                    end = next_end

            new_lines.append({
                'start': start,
                'end': end,
                'text':text
            })
           
    return new_lines


def ass_to_srt(file_in_bytes, file_name):
    raw_lines = file_in_bytes.decode('utf-8').split('\n')
    
    # remove everything but Dialogue
    lines = [l for l in raw_lines if l.startswith('Dialogue: ')]

    parsed_lines = []
    for line in lines:
        l = line.split(',')
        parsed_lines.append({
            'start': l[1].replace(".", ","), 
            'end': l[2].replace(".", ","),
            'name': l[4],
            'fx': l[8],
            'text': l[9:]
        })
    
    parsed_lines.sort(key=sort_by_time)

    # Clean text
    _del = []
    for i, line in enumerate(parsed_lines):
        text = parsed_lines[i]['text'] = parse_text(line)
        start = line['start']
        end = line['end']

        if i > 0:
            if parsed_lines[i] == parsed_lines[i-1]:
                _del.append(i)

    parsed_lines = [i for j, i in enumerate(parsed_lines) if j not in _del]

    # parsed_lines = conc_lines(parsed_lines)

    srt_events = []
    i = 0
    while i < len(parsed_lines):
        element = parsed_lines[i]
        start = element['start']
        end = element['end']
        text = element['text']
        
        # check if the end time of the current line is greater than the start time of the next line
        while i < len(parsed_lines) - 1:
            next_element = parsed_lines[i + 1]
            next_start = next_element['start']
            next_end = next_element['end']
            next_text = next_element['text']

            if end > next_start and text != next_text:
                if not '[' in next_text:
                    text += '\n—' + next_text
                else: 
                    text += '\n' + next_text
                end = next_end
                i += 1
            else:
                break          

        srt_events.append((start, end, text))
        i += 1

    todays_datetime = datetime.today().strftime('%H:%M:%S %B %d, %Y')

    # write the SRT file
    srt_text = '\n'.join([f'{i}\n{start}0 --> {end}0\n{text}\n' for i, (start, end, text) in enumerate(srt_events, 2)])
    asuna_str = f"1\n0:00:00,00 --> 0:00:00,00\nGenerated by Asuna Bot at {todays_datetime}\n\n"

    file = io.BytesIO()
    file.write(bytes(asuna_str, 'utf-8'))
    file.write(bytes(srt_text, 'utf-8'))
    file.seek(0)
    file.name = file_name.replace('.ass', '.srt')

    return file