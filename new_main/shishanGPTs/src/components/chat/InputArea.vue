<template>
  <div class="bottom">
    <label>
      <input 
        class="text-input" 
        type="text" 
        :placeholder="userInputPlaceholder" 
        :value="inputText"
        @input="onInputChange"
        @focus="clearUserInputPlaceholder" 
        @blur="resetUserInputPlaceholder" 
        @keydown.enter="sendMessage"
      >
    </label>
    <button class="send-button" v-show="!sending" @click="sendMessage">发送问题</button>
    <button class="stop-button" v-show="sending" @click="stopGeneration">停止回答</button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  sending: {
    type: Boolean,
    default: false
  }
});

// 定义emit
const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'send', 'stop']);

// 响应式数据
const inputText = ref(props.modelValue);
const userInputPlaceholder = ref('请在此输入问题...');

// 调试信息
onMounted(() => {
  console.log('InputArea mounted, initial modelValue:', props.modelValue);
});

// 监听props的变化
watch(() => props.modelValue, (newVal) => {
  console.log('modelValue changed:', newVal);
  inputText.value = newVal;
});

// 直接处理输入变化，而不是使用v-model
const onInputChange = (event) => {
  const value = event.target.value;
  console.log('Input changed:', value);
  inputText.value = value;
  emit('update:modelValue', value);
};

// 方法
const clearUserInputPlaceholder = () => {
  userInputPlaceholder.value = '';
  emit('focus');
};

const resetUserInputPlaceholder = () => {
  userInputPlaceholder.value = '请在此输入问题...';
  emit('blur');
};

const sendMessage = () => {
  console.log('Sending message with text:', inputText.value);
  if (inputText.value.trim() === '') {
    alert("输入不能为空");
    return;
  }
  emit('send');
};

const stopGeneration = () => {
  emit('stop');
};
</script>

<style scoped>
.bottom {
  margin-top: 5px;
  display: flex;
  align-self: center;
  flex-wrap: nowrap;
}

.bottom .text-input {
  padding-left: 20px;
  width: 700px;
  height: 50px;
  font-size: 16px;
  border-radius: 45px;
  border: 2px solid rgba(226, 232, 240, 1);
  outline: none;
  background: none;
  box-shadow: none;
}

.bottom .text-input:focus {
  border: 2px solid rgb(30, 150, 80);
  box-shadow: rgba(149, 240, 187, 0.1) 0 21px 8px -5px;
}

.bottom .send-button {
  margin-left: 20px;
  width: 140px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  color: #FFF;
  border-radius: 45px;
  border: none;
  box-shadow: 0 21px 27px -10px rgba(149, 240, 187, 1);
  background: linear-gradient(164.54deg, rgba(21, 89, 49, 1) 0%, rgba(1, 114, 48, 1) 92.71%);
  cursor: pointer;
}

.bottom .send-button:hover {
  background: linear-gradient(164.54deg, rgba(21, 89, 49, 0.8) 0%, rgba(1, 114, 48, 0.8) 92.71%);
}

.bottom .stop-button {
  margin-left: 10px;
  width: 140px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  color: #FFF;
  border-radius: 45px;
  border: none;
  box-shadow: 0 21px 27px -10px rgba(240, 149, 149, 1);
  background: linear-gradient(164.54deg, rgba(186, 40, 40, 1) 0%, rgba(139, 0, 0, 1) 92.71%);
  cursor: pointer;
}

.bottom .stop-button:hover {
  background: linear-gradient(164.54deg, rgba(186, 40, 40, 0.8) 0%, rgba(139, 0, 0, 0.8) 92.71%);
}
</style> 