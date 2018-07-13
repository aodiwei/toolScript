#!/usr/bin/env python3
# coding:utf-8
"""
__title__ = ''
__author__ = 'David Ao'
__mtime__ = '2018/7/6'
# 
"""
import os
import time

from fabric import Connection
from invoke import task

config = [
    dict(host='192.168.199.245', user='root', port=22, password='@@@@'),
    dict(host='192.168.199.29', user='root', port=22, password='@@@@'),
]

REMOTE_WORKSPACE = '/home/workspace/py_pro'
PRO_TAR = 'pro.tar'


def __create_conn():
    """
    创建连接
    :return:
    """
    conns = []
    for item in config:
        conn = Connection(item['host'], user=item['user'], port=item['port'], connect_kwargs=dict(password=item['password']))
        conns.append(conn)

    return conns


def walk_path(root_dir, files=None, last=None):
    """
    遍历所有文件
    :param last: 最近更新的时间，为None是忽略
    :param root_dir:
    :param files:
    :return:
    """
    files = [] if files is None else files
    for lists in os.listdir(root_dir):
        path = os.path.join(root_dir, lists)
        if os.path.isdir(path):
            walk_path(path, files, last)
        else:
            if last is not None and time.time() - os.stat(path).st_mtime > last:
                continue
            else:
                filemt = time.localtime(os.stat(path).st_mtime)
                print('{} last update time {}'.format(path, time.strftime("%Y-%m-%d %H:%M:%S", filemt)))
            files.append(path)
    return files


def put_file(conn, src):
    print('{}===========put {} to {}============'.format(conn.host, src, REMOTE_WORKSPACE))
    dst = os.path.join(REMOTE_WORKSPACE, src).replace('\\', '/')
    cmd = 'mkdir -p {}'.format(os.path.split(dst)[0])
    conn.run(cmd, warn=True)
    conn.put(src, dst)
    # print('****************finish put {}*********************************'.format(src))


@task
def pack(c):
    # 打一个tar包：
    c.run('"C:\\Program Files\\Git\\usr\\bin\\tar.exe" -cf {} ai_pro'.format(PRO_TAR))
    print('tar project')


@task
def deploy(c, p=0):
    """
    部署整个项目
    :param c:
    :return:
    """
    print('deploy whole project*************')
    assert p == 0 or p == 1
    if p:
        print('===========pack pro to tar ============')
        c.run('del {}'.format(PRO_TAR), warn=True)
        c.run('"C:\\Program Files\\Git\\usr\\bin\\tar.exe" -cf {} pro'.format(PRO_TAR))

    conns = __create_conn()
    for conn in conns:
        print('{}===========rm -rf {}============'.format(conn.host, REMOTE_WORKSPACE))
        conn.run('rm -rf {}/{}'.format(REMOTE_WORKSPACE, 'pro'), warn=True)
        print('{}===========mkdir {} ============'.format(conn.host, REMOTE_WORKSPACE))
        conn.run('mkdir -p {}'.format(REMOTE_WORKSPACE), warn=True)
        print('{}===========put tar {}============'.format(conn.host, REMOTE_WORKSPACE))
        conn.put(PRO_TAR, '{}/{}'.format(REMOTE_WORKSPACE, PRO_TAR))
        print('{}===========extract tar {}============'.format(conn.host, PRO_TAR))
        with conn.cd(REMOTE_WORKSPACE):
            conn.run('tar -xvf {}'.format(PRO_TAR))
        print('{}********************FINISH**********************************'.format(conn.host))


@task
def up_files(c, f):
    """
    更新部分文件
    :param c:
    :param f: "dir1/file2 dir2/file2"
    :return:
    """

    f = f.split(' ')
    print('update files:', f)

    conns = __create_conn()
    for conn in conns:
        for i in f:
            put_file(conn, i)


@task
def up_dir(c, d, l=None):
    """
    更新目录
    :param c:
    :param d: dir1
    :param l: 最近更新的文件
    :return:
    """
    print('update dir {} last {} second'.format(d, l))
    # return
    conns = __create_conn()
    for conn in conns:
        files = walk_path(d, last=eval(l))
        for f in files:
            put_file(conn, f)
