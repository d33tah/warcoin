all:
	pyuic4 ui/mainwindow.ui > ui/mainwindow.py	
clean:
	rm -f *.pyc ui/*.pyc
