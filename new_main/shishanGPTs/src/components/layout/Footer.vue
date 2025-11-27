<template>
  <div>
    <div class="warning">
      <span>回答由AI大模型生成，可能带有主观性和随机性，请仔细甄别！</span>
    </div>
    <div class="footer">
      <span class="copyright">© {{ currentYear }} HuaZhong Agriculture University. All Rights Reserved.</span>
      <a class="hzau-home" href="https://www.hzau.edu.cn/">访问华农官网></a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// 计算属性
const currentYear = computed(() => {
  return new Date().getFullYear();
});
</script>

<style scoped>
.warning {
  margin: 3px auto 10px;
  width: 500px;
  align-self: center;
  font-weight: 400;
  letter-spacing: 1px;
  text-align: center;
}

.footer {
  margin: 0 35px 10px 10px;
  display: flex;
  justify-content: space-between;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
  font-weight: 300;
  color: rgba(113, 128, 150, 1);
  vertical-align: top;
}

.footer .hzau-home {
  color: rgba(113, 128, 150, 1);
  text-decoration: none;
}

.footer .hzau-home:hover {
  color: #017230;
  text-decoration: underline;
}
</style> 