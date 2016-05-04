/* Minimal main program -- everything is loaded from the library. */

#include "Python.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

int WINAPI WinMain(
    HINSTANCE hInstance,      /* handle to current instance */
    HINSTANCE hPrevInstance,  /* handle to previous instance */
    LPSTR lpCmdLine,          /* pointer to command line */
    int nCmdShow              /* show state of window */
)
{
	char *command[2]={__argv[0], "libs\\sk1loader"};
	return Py_Main(2, command);
}
