<template>
  <div>
    <Header />
    <section class="cart-page flex-view">
      <div class="left-flex">
        <div class="title flex-view">
          <h3>Order details</h3>
        </div>
        <div class="cart-list-view">
          <div class="list-th flex-view">
            <span class="line-1">Dish name</span>
            <span class="line-5">number</span>
            <span class="line-6">handle</span>
          </div>
          <div class="list">
            <div class="items flex-view">
              <div class="book flex-view">
                <img :src="pageData.cover" />
                <h2>{{ pageData.title }}</h2>
              </div>
              <a-input-number v-model:value="pageData.count" :min="1" :max="10" @change="onCountChange" />
              <img :src="DeleteIcon" class="delete" />
            </div>
          </div>
        </div>
        <div class="title flex-view">
          <h3>remark</h3>
        </div>
        <textarea v-model="pageData.remark" placeholder="Enter the remarks in 100 characters or less" class="remark"> </textarea>
      </div>
      <div class="right-flex">
        <div class="title flex-view">
          <h3>Address</h3>
        </div>
        <div class="address-view">
          <div class="info" style="">
            <span>consignee：</span>
            <span class="name">{{ pageData.receiverName }} </span>
            <span class="tel">{{ pageData.receiverPhone }} </span>
          </div>
          <div class="address" v-if="pageData.receiverAddress"> {{ pageData.receiverAddress }}</div>
          <div class="info" v-else>
            <span>No address information at the moment, please</span>
            <span class="info-blue" @click="handleAdd">New address</span>
          </div>
        </div>
        <div class="price-view">
          <div class="btns-view">
            <button class="btn buy" @click="handleBack()">Return</button>
            <button class="btn pay jiesuan" @click="handleJiesuan()">Pay</button>
          </div>
        </div>
      </div>
    </section>

    <div>
      <a-modal
        :visible="modal.visile"
        :forceRender="true"
        :title="modal.title"
        ok-text="confirm"
        cancel-text="cancel"
        @cancel="handleCancel"
        @ok="handleOk"
      >
        <a-form ref="myform" :label-col="{ style: { width: '200px' } }" :model="modal.form" :rules="modal.rules">
          <a-row :gutter="24">
            <a-col span="24">
              <a-form-item label="name" name="name">
                <a-input placeholder="please input" v-model:value="modal.form.name" />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col span="24">
              <a-form-item label="phone number" name="mobile">
                <a-input placeholder="please input" v-model:value="modal.form.mobile" />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col span="24">
              <a-form-item label="delivery address" name="desc">
                <a-input placeholder="please input" v-model:value="modal.form.desc" />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="24">
            <a-col span="24">
              <a-form-item label="default address">
                <a-switch v-model:checked="modal.form.default" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { message } from 'ant-design-vue';
  import Header from '/@/views/index/components/header.vue';
  import Footer from '/@/views/index/components/footer.vue';
  import DeleteIcon from '/@/assets/images/delete-icon.svg';
  import { createApi } from '/@/api/index/order';
  import { listApi as listAddressListApi, createApi as createAddressApi } from '/@/api/index/address';
  import { useUserStore } from '/@/store';

  const router = useRouter();
  const route = useRoute();
  const userStore = useUserStore();

  const pageData = reactive({
    id: undefined,
    title: undefined,
    cover: undefined,
    price: undefined,
    remark: undefined,
    count: 1,
    amount: undefined,
    receiverName: undefined,
    receiverPhone: undefined,
    receiverAddress: undefined,
  });

  // 弹窗数据
  const modal = reactive({
    visile: false,
    editFlag: false,
    title: '',
    form: {
      name: undefined,
      mobile: undefined,
      desc: undefined,
      default: undefined,
    },
    rules: {
      name: [{ required: true, message: 'please input', trigger: 'change' }],
    },
  });

  const myform = ref();

  onMounted(() => {
    pageData.id = route.query.id;
    pageData.title = route.query.title;
    pageData.cover = route.query.cover;
    pageData.price = route.query.price;
    pageData.amount = pageData.price;

    listAddressData();
  });

  const handleAdd = () => {
    resetModal();
    modal.visile = true;
    modal.editFlag = false;
    modal.title = 'add new';
    // 重置
    for (const key in modal.form) {
      modal.form[key] = undefined;
    }
  };

  const handleOk = () => {
    if (!userStore.user_id) {
      message.warn('please login firsst');
      return;
    }
    myform.value
      ?.validate()
      .then(() => {
        const formData = new FormData();
        formData.append('user', userStore.user_id);
        formData.append('default', modal.form.default ? 'true' : 'false');
        if (modal.form.name) {
          formData.append('name', modal.form.name);
        }
        if (modal.form.mobile) {
          formData.append('mobile', modal.form.mobile);
        }
        if (modal.form.desc) {
          formData.append('desc', modal.form.desc);
        }
        createAddressApi(formData)
          .then((res) => {
            console.log(res);
            hideModal();
            pageData.receiverName = modal.form.name;
            pageData.receiverAddress = modal.form.desc;
            pageData.receiverPhone = modal.form.mobile;
          })
          .catch((err) => {
            message.error(err.msg || 'add new fail');
          });
      })
      .catch((err) => {
        console.log(err);
        console.log('can not be null');
      });
  };

  const handleCancel = () => {
    hideModal();
  };

  const resetModal = () => {
    myform.value?.resetFields();
  };

  const hideModal = () => {
    modal.visile = false;
  };

  const onCountChange = (value) => {
    pageData.amount = pageData.price * value;
  };

  const listAddressData = () => {
    let userId = userStore.user_id;
    listAddressListApi({ userId: userId })
      .then((res) => {
        if (res.data.length > 0) {
          pageData.receiverName = res.data[0].name;
          pageData.receiverPhone = res.data[0].mobile;
          pageData.receiverAddress = res.data[0].desc;
          res.data.forEach((item) => {
            if (item.default) {
              pageData.receiverName = item.name;
              pageData.receiverPhone = item.mobile;
              pageData.receiverAddress = item.desc;
            }
          });
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const handleBack = () => {
    router.back();
    console.log('back...');
  };
  const handleJiesuan = () => {
    const formData = new FormData();
    let userId = userStore.user_id;
    if (!userId) {
      message.warn('please login first！');
      return;
    }
    if (!pageData.receiverName) {
      message.warn('please select your address！');
      return;
    }
    formData.append('user', userId);
    formData.append('thing', pageData.id);
    formData.append('count', pageData.count);
    if (pageData.remark) {
      formData.append('remark', pageData.remark);
    }
    formData.append('receiver_name', pageData.receiverName);
    formData.append('receiver_phone', pageData.receiverPhone);
    formData.append('receiver_address', pageData.receiverAddress);
    console.log(formData);
    createApi(formData)
      .then((res) => {
        router.push({ name: 'pay', query: { amount: pageData.amount } });
      })
      .catch((err) => {
        message.error(err.msg || '失败');
      });
  };
</script>

<style scoped lang="less">
  .flex-view {
    display: -webkit-box;
    display: -ms-flexbox;
    display: flex;
  }

  .cart-page {
    width: 1024px;
    min-height: 50vh;
    margin: 100px auto;
  }

  .left-flex {
    -webkit-box-flex: 17;
    -ms-flex: 17;
    flex: 17;
    padding-right: 20px;
  }

  .title {
    -webkit-box-pack: justify;
    -ms-flex-pack: justify;
    justify-content: space-between;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;

    h3 {
      color: #152844;
      font-weight: 600;
      font-size: 18px;
      height: 26px;
      line-height: 26px;
      margin: 0;
    }
  }

  .cart-list-view {
    margin: 4px 0 40px;

    .list-th {
      height: 42px;
      line-height: 42px;
      border-bottom: 1px solid #cedce4;
      color: #152844;
      font-size: 14px;

      .line-1 {
        -webkit-box-flex: 1;
        -ms-flex: 1;
        flex: 1;
        margin-right: 20px;
      }

      .line-2,
      .pc-style .cart-list-view .list-th .line-3,
      .pc-style .cart-list-view .list-th .line-4 {
        width: 65px;
        margin-right: 20px;
      }

      .line-5 {
        width: 80px;
        margin-right: 40px;
      }

      .line-6 {
        width: 28px;
      }
    }
  }

  .items {
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    margin-top: 20px;

    .book {
      -webkit-box-flex: 1;
      -ms-flex: 1;
      flex: 1;
      -webkit-box-align: center;
      -ms-flex-align: center;
      align-items: center;
      margin-right: 20px;
      cursor: pointer;

      img {
        width: 48px;
        margin-right: 16px;
        border-radius: 4px;
      }

      h2 {
        -webkit-box-flex: 1;
        -ms-flex: 1;
        flex: 1;
        font-size: 14px;
        line-height: 22px;
        color: #152844;
      }
    }

    .type {
      width: 65px;
      margin-right: 20px;
      color: #152844;
      font-size: 14px;
    }

    .pay {
      color: #ff8a00;
      font-weight: 600;
      font-size: 16px;
      width: 65px;
      margin-right: 20px;
    }

    .num-box {
      width: 80px;
      margin-right: 43px;
      border-radius: 4px;
      border: 1px solid #cedce4;
      -webkit-box-pack: justify;
      -ms-flex-pack: justify;
      justify-content: space-between;
      -webkit-box-align: center;
      -ms-flex-align: center;
      align-items: center;
      height: 32px;
      padding: 0 4px;
    }

    .delete {
      margin-left: 36px;
      width: 24px;
      cursor: pointer;
    }
  }

  .mb-24 {
    margin-bottom: 24px;
  }

  .show-txt {
    color: #ff8a00;
    font-size: 14px;
  }

  .remark {
    width: 100%;
    background: #f6f9fb;
    border: 0;
    border-radius: 4px;
    padding: 6px 12px;
    //color: #152844;
    margin-top: 16px;
    resize: none;
    height: 56px;
    line-height: 22px;
  }

  .right-flex {
    -webkit-box-flex: 8;
    -ms-flex: 8;
    flex: 8;
    padding-left: 24px;
    border-left: 1px solid #cedce4;
  }

  .click-txt {
    color: #4684e2;
    font-size: 14px;
    cursor: pointer;
  }

  .address-view {
    margin: 12px 0 24px;

    .info {
      color: #909090;
      font-size: 14px;

      .info-blue {
        cursor: pointer;
        color: #4684e2;
      }
    }

    .name {
      color: #152844;
      font-weight: 500;
    }

    .tel {
      color: #152844;
      float: right;
    }

    .address {
      color: #152844;
      margin-top: 4px;
    }
  }

  .price-view {
    overflow: hidden;
    margin-top: 16px;

    .price-item {
      -webkit-box-pack: justify;
      -ms-flex-pack: justify;
      justify-content: space-between;
      -webkit-box-align: center;
      -ms-flex-align: center;
      align-items: center;
      margin-bottom: 8px;
      font-size: 14px;

      .item-name {
        color: #152844;
      }

      .price-txt {
        font-weight: 500;
        color: #ff8a00;
      }
    }

    .total-price-view {
      margin-top: 12px;
      border-top: 1px solid #cedce4;
      -webkit-box-pack: justify;
      -ms-flex-pack: justify;
      justify-content: space-between;
      -webkit-box-align: start;
      -ms-flex-align: start;
      align-items: flex-start;
      padding-top: 10px;
      color: #152844;
      font-weight: 500;

      .price {
        color: #ff8a00;
        font-size: 16px;
        height: 36px;
        line-height: 36px;
      }
    }

    .btns-view {
      margin-top: 24px;
      text-align: right;

      .buy {
        background: #fff;
        color: #4684e2;
      }

      .jiesuan {
        cursor: pointer;
        background: #4684e2;
        color: #fff;
      }

      .btn {
        cursor: pointer;
        width: 96px;
        height: 36px;
        line-height: 33px;
        margin-left: 16px;
        text-align: center;
        border-radius: 32px;
        border: 1px solid #4684e2;
        font-size: 16px;
        outline: none;
      }
    }
  }
</style>
