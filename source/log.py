import time
import  os
class LOG:
    def getsize(self,file):
        # print(type(os.stat(file)[6]))
        return os.stat(file)[6]

    def rename(self,last,new):
        os.rename(last,new)

    def remove(self,file):
        os.remove(file)

    def logging(self, func):
        import sys
        def _deco():
            try:
                func()
            except Exception as e:
                size = self.getsize('new.log')
                if size > 10 * 1024:
                    self.rename('new.log','_new.log')
                    self.rename('last.log','new.log')
                    self.rename('_new.log','last.log')
                    with open("new.log", "w") as f:
                        f.write(str(time.time())+'\r\n')
                        sys.print_exception(e, f)
                else:
                    with open("new.log", "a") as f:
                        f.write(str(time.time())+'\r\n')
                        sys.print_exception(e, f)
        return _deco

ts=LOG()
@ts.logging
def bar():
    raise ValueError
    print('this is test output run.log')
    # c = e


# while True:
#     bar()
#     import utime
#     utime.sleep_ms(1000)
# # ts=LOG()
# ts.getsize('boot.py')
