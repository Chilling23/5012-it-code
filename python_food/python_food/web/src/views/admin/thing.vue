<template>
  <div>

    <div class="page-view">
      <div class="table-operations">
        <a-space>
          <a-button type="primary" @click="handleAdd">add new</a-button>
          <a-button @click="handleBatchDelete">delete in batches</a-button>
          <a-input-search addon-before="name" enter-button @search="onSearch" @change="onSearchChange" />
        </a-space>
      </div>
      <a-table
        size="middle"
        rowKey="id"
        :loading="data.loading"
        :columns="columns"
        :data-source="data.dataList"
        :scroll="{ x: 'max-content' }"
        :row-selection="rowSelection"
        :pagination="{
          size: 'default',
          current: data.page,
          pageSize: data.pageSize,
          onChange: (current) => (data.page = current),
          showSizeChanger: false,
          showTotal: (total) => `${total} data in total`,
        }"
      >
        <template #bodyCell="{ text, record, index, column }">
          <template v-if="column.key === 'operation'">
            <span>
              <a @click="handleEdit(record)">edit</a>
              <a-divider type="vertical" />
              <a-popconfirm title="are you sure to delete?" ok-text="yes" cancel-text="no" @confirm="confirmDelete(record)">
                <a href="#">delete</a>
              </a-popconfirm>
            </span>
          </template>
        </template>
      </a-table>
    </div>

    <div>
      <a-modal
        :visible="modal.visile"
        :forceRender="true"
        :title="modal.title"
        width="880px"
        ok-text="confirm"
        cancel-text="cancel"
        @cancel="handleCancel"
        @ok="handleOk"
      >
        <div>
          <a-form ref="myform" :label-col="{ style: { width: '80px' } }" :model="modal.form" :rules="modal.rules">
            <a-row :gutter="24">
              <a-col span="24">
                <a-form-item label="dish name" name="title">
                  <a-input placeholder="please input" v-model:value="modal.form.title" />
                </a-form-item>
              </a-col>
              <a-col span="12">
                <a-form-item label="category" name="classification">
                  <a-select
                    placeholder="please select"
                    allowClear
                    :options="modal.cData"
                    :field-names="{ label: 'title', value: 'id' }"
                    v-model:value="modal.form.classification"
                  />
                </a-form-item>
              </a-col>
              <a-col span="12">
                <a-form-item label="label">
                  <a-select mode="multiple" placeholder="please select" allowClear v-model:value="modal.form.tag">
                    <template v-for="item in modal.tagData">
                      <a-select-option :value="item.id">{{ item.title }}</a-select-option>
                    </template>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col span="24">
                <a-form-item label="cover">
                  <a-upload-dragger
                    name="file"
                    accept="image/*"
                    :multiple="false"
                    :before-upload="beforeUpload"
                    v-model:file-list="fileList"
                  >
                    <p class="ant-upload-drag-icon">
                      <template v-if="modal.form.coverUrl">
                        <img :src="modal.form.coverUrl" style="width: 60px; height: 80px" />
                      </template>
                      <template v-else>
                        <file-image-outlined />
                      </template>
                    </p>
                    <p class="ant-upload-text"> Please select the cover image you want to upload </p>
                  </a-upload-dragger>
                </a-form-item>
              </a-col>

              <a-col span="24">
                <a-form-item label="introduction">
                  <a-textarea placeholder="please select" v-model:value="modal.form.description" />
                </a-form-item>
              </a-col>
              <a-col span="12">
                <a-form-item label="price" name="price">
                  <a-input-number placeholder="please input" :min="0" v-model:value="modal.form.price" style="width: 100%" />
                </a-form-item>
              </a-col>
              <a-col span="12">
                <a-form-item label="state" name="status">
                  <a-select placeholder="please select" allowClear v-model:value="modal.form.status">
                    <a-select-option key="0" value="0">added</a-select-option>
                    <a-select-option key="1" value="1">sold out</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </div>
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { FormInstance, message, SelectProps } from 'ant-design-vue';
  import { createApi, listApi, updateApi, deleteApi } from '/@/api/admin/thing';
  import { listApi as listClassificationApi } from '/@/api/admin/classification';
  import { listApi as listTagApi } from '/@/api/admin/tag';
  import { BASE_URL } from '/@/store/constants';
  import { FileImageOutlined } from '@ant-design/icons-vue';

  const columns = reactive([
    {
      title: 'serial',
      dataIndex: 'index',
      key: 'index',
      width: 60,
    },
    {
      title: 'name',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'price',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'state',
      dataIndex: 'status',
      key: 'status',
      customRender: ({ text, record, index, column }) => (text === '0' ? 'added' : 'sold out'),
    },
    {
      title: 'description',
      dataIndex: 'description',
      key: 'description',
      customRender: ({ text, record, index, column }) => (text ? text.substring(0, 10) + '...' : '--'),
    },
    {
      title: 'action',
      dataIndex: 'action',
      key: 'operation',
      align: 'center',
      fixed: 'right',
      width: 140,
    },
  ]);

  const beforeUpload = (file: File) => {
    // change file name
    const fileName = new Date().getTime().toString() + '.' + file.type.substring(6);
    const copyFile = new File([file], fileName);
    console.log(copyFile);
    modal.form.imageFile = copyFile;
    return false;
  };

  // document list
  const fileList = ref<any[]>([]);

  // page data
  const data = reactive({
    dataList: [],
    loading: false,
    keyword: '',
    selectedRowKeys: [] as any[],
    pageSize: 10,
    page: 1,
  });

  // data source
  const modal = reactive({
    visile: false,
    editFlag: false,
    title: '',
    cData: [],
    tagData: [{}],
    form: {
      id: undefined,
      title: undefined,
      nickname: undefined,
      classification: undefined,
      tag: [],
      repertory: undefined,
      price: undefined,
      status: undefined,
      cover: undefined,
      coverUrl: undefined,
      imageFile: undefined,
    },
    rules: {
      title: [{ required: true, message: '请输入名称', trigger: 'change' }],
      classification: [{ required: true, message: '请选择分类', trigger: 'change' }],
      repertory: [{ required: true, message: '请输入库存', trigger: 'change' }],
      price: [{ required: true, message: '请输入定价', trigger: 'change' }],
      status: [{ required: true, message: '请选择状态', trigger: 'change' }],
    },
  });

  const myform = ref<FormInstance>();

  onMounted(() => {
    getDataList();
    getCDataList();
    getTagDataList();
  });

  const getDataList = () => {
    data.loading = true;
    listApi({
      keyword: data.keyword,
    })
      .then((res) => {
        data.loading = false;
        console.log(res);
        res.data.forEach((item: any, index: any) => {
          item.index = index + 1;
        });
        data.dataList = res.data;
      })
      .catch((err) => {
        data.loading = false;
        console.log(err);
      });
  };

  const getCDataList = () => {
    listClassificationApi({}).then((res) => {
      modal.cData = res.data;
    });
  };
  const getTagDataList = () => {
    listTagApi({}).then((res) => {
      res.data.forEach((item, index) => {
        item.index = index + 1;
      });
      modal.tagData = res.data;
    });
  };

  const onSearchChange = (e: Event) => {
    data.keyword = e?.target?.value;
    console.log(data.keyword);
  };

  const onSearch = () => {
    getDataList();
  };

  const rowSelection = ref({
    onChange: (selectedRowKeys: (string | number)[], selectedRows: DataItem[]) => {
      console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
      data.selectedRowKeys = selectedRowKeys;
    },
  });

  const handleAdd = () => {
    resetModal();
    modal.visile = true;
    modal.editFlag = false;
    modal.title = 'add';
    // reset
    for (const key in modal.form) {
      modal.form[key] = undefined;
    }
    modal.form.cover = undefined;
  };
  const handleEdit = (record: any) => {
    resetModal();
    modal.visile = true;
    modal.editFlag = true;
    modal.title = 'edit';
    // reset
    for (const key in modal.form) {
      modal.form[key] = undefined;
    }
    for (const key in record) {
      if (record[key]) {
        modal.form[key] = record[key];
      }
    }
    if (modal.form.cover) {
      modal.form.coverUrl = BASE_URL + modal.form.cover;
      modal.form.cover = undefined;
    }
  };

  const confirmDelete = (record: any) => {
    console.log('delete', record);
    deleteApi({ ids: record.id })
      .then((res) => {
        getDataList();
      })
      .catch((err) => {
        message.error(err.msg || 'operation fail');
      });
  };

  const handleBatchDelete = () => {
    console.log(data.selectedRowKeys);
    if (data.selectedRowKeys.length <= 0) {
      console.log('hello');
      message.warn('please select delete item');
      return;
    }
    deleteApi({ ids: data.selectedRowKeys.join(',') })
      .then((res) => {
        message.success('delete successfully');
        data.selectedRowKeys = [];
        getDataList();
      })
      .catch((err) => {
        message.error(err.msg || 'operation fail');
      });
  };

  const handleOk = () => {
    myform.value
      ?.validate()
      .then(() => {
        const formData = new FormData();
        if (modal.editFlag) {
          formData.append('id', modal.form.id);
        }
        formData.append('title', modal.form.title);
        if (modal.form.classification) {
          formData.append('classification', modal.form.classification);
        }
        if (modal.form.tag) {
          modal.form.tag.forEach(function (value) {
            if (value) {
              formData.append('tag', value);
            }
          });
        }
        if (modal.form.imageFile) {
          formData.append('cover', modal.form.imageFile);
        }
        formData.append('description', modal.form.description || '');
        formData.append('price', modal.form.price || '');

        if (modal.form.status) {
          formData.append('status', modal.form.status);
        }
        if (modal.editFlag) {
          updateApi(
            {
              id: modal.form.id,
            },
            formData,
          )
            .then((res) => {
              hideModal();
              getDataList();
            })
            .catch((err) => {
              console.log(err);
              message.error(err.msg || 'operation fail');
            });
        } else {
          createApi(formData)
            .then((res) => {
              hideModal();
              getDataList();
            })
            .catch((err) => {
              console.log(err);
              message.error(err.msg || 'operation fail');
            });
        }
      })
      .catch((err) => {
        console.log('can not be null');
      });
  };

  const handleCancel = () => {
    hideModal();
  };


  const resetModal = () => {
    myform.value?.resetFields();
    fileList.value = [];
  };

  const hideModal = () => {
    modal.visile = false;
  };
</script>

<style scoped lang="less">
  .page-view {
    min-height: 100%;
    background: #fff;
    padding: 24px;
    display: flex;
    flex-direction: column;
  }

  .table-operations {
    margin-bottom: 16px;
    text-align: right;
  }

  .table-operations > button {
    margin-right: 8px;
  }
</style>
