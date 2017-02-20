"""
https://gist.github.com/nghuuphuoc/7801123
// --- Compiling ---
$ wget http://download.redis.io/releases/redis-2.8.3.tar.gz
$ tar xzvf redis-2.8.3.tar.gz
$ cd redis-2.8.3
$ make
$ make install

// --- or using yum ---
$ rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
$ rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-6.rpm

$ yum --enablerepo=remi,remi-test install redis
"""