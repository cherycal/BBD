__author__ = 'chance'

# import html
import sys
sys.path.append('../modules')
from git import Repo


#inst = push.Push()
sleep_interval = 1.0

gitfile_name = "site/mobile/stub.html"
outfile_name = "/media/sf_Shared/first/site/mobile/stub.html"


repo = Repo("C:\\Ubuntu\\Shared\\BBD")
assert not repo.bare
git = repo.git

print(repo.git.status("-s"))
#
# flag = 0
#
# git.add(gitfile_name)
# time.sleep(sleep_interval)
# git.commit('-m','update',gitfile_name)
# time.sleep(sleep_interval)
# git.push()

