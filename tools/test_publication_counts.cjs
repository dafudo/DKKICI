const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const word=require('../js/publication-count.js');
for(const [n,w] of [[0,'publikacji'],[1,'publikacja'],[2,'publikacje'],[3,'publikacje'],[4,'publikacje'],[5,'publikacji'],[11,'publikacji'],[12,'publikacji'],[14,'publikacji'],[21,'publikacji'],[22,'publikacje'],[25,'publikacji'],[101,'publikacji'],[102,'publikacje'],[112,'publikacji'],[122,'publikacje']])assert.equal(word(n,'pl'),w,'Count '+n);
assert.equal(word(1,'en'),'publication');
assert.equal(word(2,'en'),'publications');
assert.throws(()=>word(-1,'pl'),RangeError);
for(const p of ['publications/index.html','pl/publikacje/index.html']){
 const h=fs.readFileSync(path.join(__dirname,'..',p),'utf8');
 assert.match(h,/data-publication-word/);
 assert.match(h,/js\/publication-count\.js/);
}
console.log('PASS: publication declension');
