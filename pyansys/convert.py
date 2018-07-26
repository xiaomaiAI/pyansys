import os
import pyansys

valid_functions = dir(pyansys.ANSYS)


def IsFloat(string):
    """ Returns true when a string can be converted to a float """
    try:
        float(string)
        return True
    except:
        return False


def ConvertLine(line, obj='ansys', line_ending='\n'):
    """ Converts a single line from an ANSYS APDL script """
    line = line.rstrip()
    line = line.replace('"', "'")
    # check if it's a command

    items = line.split(',')
    if '=' in items[0]:  # line sets a variable:
        return '%s.Run("%s")%s' % (obj, line, line_ending)
    # elif 'C***' in items[0]:  # line is a comment
        # return '%s.Run("%s")\n' % (obj, line)
    elif '!' in items[0]:  # line contains a comment
        if items[0].strip()[0] == '!':
            return '%s%s' % (line.replace('!', '#'), line_ending)

    command = items[0].capitalize().strip()
    if not command:
        return (line_ending)

    # check if first item is a valid command
    if command not in valid_functions:
        if '/COM' in line:
            return line.replace('/COM', '# ') + line_ending
        # elif 'VWRITE' in line:  # ignore vwrite prompts (ansys verification files)
            # return '%s.Run("%s", ignore_prompt=True)%s' % (obj, line, line_ending)
        elif '*CREATE' in line:  # now writing to macro
            newline = '%s.block_override = False%s' % (obj, line_ending)
            newline += '%s.Run("%s")%s' % (obj, line, line_ending)
            return newline
        elif '*END' in line and '*ENDIF' not in line:  # stop writing to macro
            newline = '%s.Run("%s")%s' % (obj, line, line_ending)
            newline += '%s.block_override = None%s' % (obj, line_ending)
            return newline
        else:
            return '%s.Run("%s")%s' % (obj, line, line_ending)

    converted_line = '%s.%s(' % (obj, command)
    items = items[1:]
    for i, item in enumerate(items):
        if IsFloat(item):
            items[i] = item.strip()
        else:
            items[i] = '"%s"' % item.strip()

    converted_line += ', '.join(items)
    if 'VWRITE' in converted_line:
        converted_line += ', ignore_prompt=True)%s' % line_ending
    else:
        converted_line += ')%s' % line_ending

    return converted_line


def ConvertFile(filename_in, filename_out, loglevel='INFO', auto_exit=True,
                line_ending=None):
    """
    Converts an ANSYS input file to a python pyansys script.

    Parameters
    ----------
    filename_in : str
        Filename of the ansys input file to read in.

    filename_out : str
        Filename of the python script to write a translation to.

    loglevel : str, optional
        Log level of the ansys object within the script.

    auto_exit : bool, optional
        Adds a line to the end of the script to exit ANSYS.  Default True.

    line_ending : str, optional
        When None, automatically determined by OS being used.  
        Acceptable inputs are:

        - \n
        - \r\n

    Returns
    -------
    clines : list
        List of lines translated

    """
    if line_ending is None:
        line_ending = os.linesep
    elif line_ending not in ['\n', '\r\n']:
        raise Exception('Line ending must be either "\\n", "\\r\\n"')

    clines = []
    with open(filename_in) as file_in:
        with open(filename_out, 'w') as file_out:
            # obligatory lines
            line = '""" Script generated by pyansys version %s"""%s' % (pyansys.__version__,
                                                                        line_ending)
            file_out.write(line)
            clines.append(line)

            line = 'import pyansys%s' % line_ending
            file_out.write(line)
            clines.append(line)

            line = 'ansys = pyansys.ANSYS(loglevel="%s")%s' % (loglevel, line_ending)
            file_out.write(line)
            clines.append(line)

            for line in file_in.readlines():
                cline = ConvertLine(line)
                file_out.write(cline)
                clines.append(cline)

            cline = 'ansys.Exit()%s' % line_ending
            file_out.write(cline)
            clines.append(cline)

    return clines
