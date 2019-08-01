from django.db import models
from juser.models import User
import time


class ManagerLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100)
    msg = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.type




class Log(models.Model):
    user = models.CharField(max_length=20, null=True)
    host = models.CharField(max_length=200, null=True)
    remote_ip = models.CharField(max_length=100)
    login_type = models.CharField(max_length=100)
    log_path = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True)
    pid = models.IntegerField()
    is_finished = models.BooleanField(default=False)
    end_time = models.DateTimeField(null=True)
    filename = models.CharField(max_length=40)
    '''
    add by liuzheng
    '''
    # userMM = models.ManyToManyField(User)
    # logPath = models.TextField()
    # filename = models.CharField(max_length=40)
    # logPWD = models.TextField()  # log zip file's
    # nick = models.TextField(null=True)  # log's nick name
    # log = models.TextField(null=True)
    # history = models.TextField(null=True)
    # timestamp = models.IntegerField(default=int(time.time()))
    # datetimestamp = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.log_path


class Alert(models.Model):
    msg = models.CharField(max_length=20)
    time = models.DateTimeField(null=True)
    is_finished = models.BigIntegerField(default=False)


class TtyLog(models.Model):
    log = models.ForeignKey(Log)
    datetime = models.DateTimeField(auto_now=True)
    cmd = models.CharField(max_length=200)


class ExecLog(models.Model):
    user = models.CharField(max_length=100)
    host = models.TextField()
    cmd = models.TextField()
    remote_ip = models.CharField(max_length=100)
    result = models.TextField(default='')
    datetime = models.DateTimeField(auto_now=True)


class FileLog(models.Model):
    user = models.CharField(max_length=100)
    host = models.TextField()
    filename = models.TextField()
    type = models.CharField(max_length=20)
    remote_ip = models.CharField(max_length=100)
    result = models.TextField(default='')
    datetime = models.DateTimeField(auto_now=True)


class TermLog(models.Model):
    # user = models.ManyToManyField(User)
    logPath = models.TextField()
    filename = models.CharField(max_length=40)
    logPWD = models.TextField()  # log zip file's
    nick = models.TextField(null=True)  # log's nick name
    log = models.TextField(null=True)
    history = models.TextField(null=True)
    timestamp = models.IntegerField(default=int(time.time()))
    datetimestamp = models.DateTimeField(auto_now_add=True)

#
# #私链区块链 区块
# class PrivateBlockChainLog(models.Model):
#     id = models.IntegerField(primary_key=True)
#     number = models.IntegerField()
#     hash = models.CharField(max_length=256)
#     difficulty = models.IntegerField()
#     extraData = models.TextField()
#     gasLimit = models.IntegerField()
#     gasUsed = models.IntegerField()
#     logsBloom = models.TextField()
#     miner = models.CharField(max_length=256)
#     mixHash = models.CharField(max_length=256)
#     nonce = models.CharField(max_length=256)
#     parentHash = models.CharField(max_length=256)
#     receiptsRoot = models.CharField(max_length=256)
#     sha3Uncles = models.CharField(max_length=256)
#     size = models.IntegerField()
#     stateRoot = models.CharField(max_length=256)
#     timestamp = models.DateTimeField()
#     totalDifficulty = models.BigIntegerField()
#     transactions = models.TextField()
#     transactionsRoot = models.CharField(max_length=256)
#     uncles = models.TextField()

# #私链区块 交易信息
# class PrivateBlockChainTransactionLog(models.Model):
#     id = models.AutoField(primary_key=True)
#     blockNumber = models.IntegerField()
#     blockHash = models.CharField(max_length=256)
#     from_addr = models.CharField(max_length=256)
#     to_addr = models.CharField(max_length=256)
#     gas = models.IntegerField()
#     gasPrice = models.BigIntegerField()
#     hash = models.CharField(max_length=256)
#     input = models.TextField()
#     nonce = models.IntegerField()
#     transactionIndex = models.IntegerField()
#     value = models.CharField(max_length=256)
#     v = models.BigIntegerField()
#     r = models.TextField()
#     s = models.TextField()
#     block = models.ForeignKey(PrivateBlockChainLog,
#                             related_name='trans_block_number_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块')
# #BidOK 事件
# class PBEventBidOK(models.Model):
#     id = models.AutoField(primary_key=True)
#     event = models.CharField(max_length=256)
#     blockNumber = models.IntegerField()
#     blockHash = models.CharField(max_length=256)
#     address = models.CharField(max_length=256)
#     transactionHash = models.CharField(max_length=256)
#     transactionIndex = models.IntegerField()
#     logIndex = models.IntegerField()
#     arg_from = models.CharField(max_length=256)
#     arg_to = models.CharField(max_length=256)
#     arg_value = models.CharField(max_length=256)
#     block = models.ForeignKey(PrivateBlockChainLog,
#                             related_name='evtbidok_block_number_',
#                             blank=True,
#                             null=True,
#                             verbose_name=u'区块')
#     transaction = models.ForeignKey(PrivateBlockChainTransactionLog,
#                             related_name='evtbidok_trans_id_',
#                             blank=True,
#                             null=True,
#                             verbose_name=u'区块交易条目')
# #GameBid 事件
# class PBEventGameBid(models.Model):
#     id = models.AutoField(primary_key=True)
#     event = models.CharField(max_length=256)
#     blockNumber = models.IntegerField()
#     blockHash = models.CharField(max_length=256)
#     address = models.CharField(max_length=256)
#     transactionHash = models.CharField(max_length=256)
#     transactionIndex = models.IntegerField()
#     logIndex = models.IntegerField()
#     arg_gameid = models.IntegerField()
#     arg_from = models.CharField(max_length=256)
#     arg_value = models.CharField(max_length=256)
#     arg_bet = models.IntegerField()
#     arg_rate = models.IntegerField()
#     block = models.ForeignKey(PrivateBlockChainLog,
#                             related_name='evtgamebid_block_number_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块')
#     transaction = models.ForeignKey(PrivateBlockChainTransactionLog,
#                             related_name='evtgamebid_trans_id_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块交易条目')

# #WinBid 事件
# class PBEventWinBid(models.Model):
#     id = models.AutoField(primary_key=True)
#     event = models.CharField(max_length=256)
#     blockNumber = models.IntegerField()
#     blockHash = models.CharField(max_length=256)
#     address = models.CharField(max_length=256)
#     transactionHash = models.CharField(max_length=256)
#     transactionIndex = models.IntegerField()
#     logIndex = models.IntegerField()
#     arg_to = models.CharField(max_length=256)
#     arg_value = models.CharField(max_length=256)
#     block = models.ForeignKey(PrivateBlockChainLog,
#                             related_name='evtwinbid_block_number_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块')
#     transaction = models.ForeignKey(PrivateBlockChainTransactionLog,
#                             related_name='evtwinbid_trans_id_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块交易条目')

# #Ratok 事件
# class PBEventRatok(models.Model):
#     id = models.AutoField(primary_key=True)
#     event = models.CharField(max_length=256)
#     blockNumber = models.IntegerField()
#     blockHash = models.CharField(max_length=256)
#     address = models.CharField(max_length=256)
#     transactionHash = models.CharField(max_length=256)
#     transactionIndex = models.IntegerField()
#     logIndex = models.IntegerField()
#     arg_gameid = models.IntegerField()
#     arg_bet_no = models.IntegerField()
#     arg_rate = models.BigIntegerField()
#     block = models.ForeignKey(PrivateBlockChainLog,
#                             related_name='evtratok_block_number_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块')
#     transaction = models.ForeignKey(PrivateBlockChainTransactionLog,
#                             related_name='evtratok_trans_id_',
#                             blank=True,
#                             null=True,
#                             verbose_name='区块交易条目')
