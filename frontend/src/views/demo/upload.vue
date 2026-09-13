<!-- 文件上传组件示例 -->
<template>
  <PageShell class="ff-demo-page">
    <el-form>
      <el-form-item label="单图上传">
        <SingleImageUpload v-model="picUrl" />
      </el-form-item>

      <el-form-item label="多图上传">
        <MultiImageUpload v-model="picUrls" :limit="2" />
      </el-form-item>

      <el-form-item label="文件上传">
        <FileUpload v-model="fileUrls" />
      </el-form-item>
    </el-form>
  </PageShell>
</template>

<script setup lang="ts">
import PageShell from "@/components/PageShell/index.vue";
import MultiImageUpload from "@/components/Upload/MultiImageUpload.vue";

// 单图
const picUrl = ref("https://s2.loli.net/2023/05/24/yNsxFC8rLHMZQcK.jpg");
const picUrls = ref(["https://s2.loli.net/2023/05/24/yNsxFC8rLHMZQcK.jpg"]);

const fileUrls = ref([
  { name: "照片1.jpg", url: "https://s2.loli.net/2023/05/24/yNsxFC8rLHMZQcK.jpg" },
  { name: "照片2.jpg", url: "https://s2.loli.net/2023/05/24/RuHFMwW4rG5lIqs.jpg" },
]);
</script>
