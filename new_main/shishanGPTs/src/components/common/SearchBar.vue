<template>
  <div class="search-area">
    <i class="search-icon"></i>
    <label>
      <input 
        class="search-input" 
        type="search" 
        :placeholder="searchPlaceholder" 
        :value="searchText"
        @input="onInputChange"
        @focus="clearSearchPlaceholder" 
        @blur="resetSearchPlaceholder"
      >
    </label>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// 定义props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
});

// 定义emit
const emit = defineEmits(['update:modelValue', 'focus', 'blur']);

// 响应式数据
const searchText = ref(props.modelValue);
const searchPlaceholder = ref('搜索华农官网信息');

// 监听props的变化
watch(() => props.modelValue, (newVal) => {
  searchText.value = newVal;
});

// 直接处理输入变化
const onInputChange = (event) => {
  const value = event.target.value;
  searchText.value = value;
  emit('update:modelValue', value);
};

// 方法
const clearSearchPlaceholder = () => {
  searchPlaceholder.value = '';
  emit('focus');
};

const resetSearchPlaceholder = () => {
  searchPlaceholder.value = '搜索华农官网信息';
  emit('blur');
};
</script>

<style scoped>
.search-area {
  position: relative;
  width: 205px;
  height: 36px;
  border-radius: 40px;
  background: rgba(244, 247, 254, 1);
}

.search-area .search-icon {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 15px;
  margin: auto 0;
  display: block;
  width: 11px;
  height: 11px;
  background: url(@/assets/images/icon_search.png) no-repeat;
}

.search-area .search-input {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 35px;
  margin: auto 0;
  height: 20px;
  line-height: 20px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 1px;
  color: rgba(113, 128, 150, 1);
  outline: none;
  border: none;
  background: none;
  box-shadow: none;
}
</style> 