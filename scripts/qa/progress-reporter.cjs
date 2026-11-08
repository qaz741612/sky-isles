// Bounded progress to disk, never full test logs/binary in the chat.
const fs=require('node:fs');
module.exports=class Progress{
 onTestEnd(test,result){
  const path=process.env.SKYISLES_QA_PROGRESS;if(!path)return;
  fs.appendFileSync(path,JSON.stringify({title:test.title,project:test.parent.project()?.name,status:result.status,duration:result.duration,retry:result.retry,error:result.error?.message?.slice(0,500)})+'\n');
 }
};
