<script setup>
import { ref } from 'vue';

const data = ref(null)
const tempData = ref(null)

const fileInput =ref(null)
const showUpload =ref(false)


function uploadFile(){
    const formData = new FormData();
    formData.append('file', fileInput.value.files[0]);

    fetch('http://localhost:8000/file', {
        method: 'POST', 
        body: formData
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((resp) => {
        data.value = resp
        tempData.value = JSON.parse(JSON.stringify(data.value))
    });
}

const isFirstDivision = (key) => Object.keys(tempData.value.divisions)[0] === key;
const isLastDivision = (key) => Object.keys(tempData.value.divisions).slice(-1)[0] === key;

const moveItem = (key, direction) => {
  const divisionKeys = Object.keys(tempData.value.divisions);
  if (direction === 'up' && !isFirstDivision(key)) {
    const currentIndex = divisionKeys.indexOf(key);   
    [divisionKeys[currentIndex - 1], divisionKeys[currentIndex]] = [divisionKeys[currentIndex], divisionKeys[currentIndex - 1]];
  } 
  else if (direction === 'down' && !isLastDivision(key)) {
    const currentIndex = divisionKeys.indexOf(key);
    [divisionKeys[currentIndex + 1], divisionKeys[currentIndex]] = [divisionKeys[currentIndex], divisionKeys[currentIndex + 1]];
  }

  const newDivisions = {};
  divisionKeys.forEach((divisionKey) => {
    newDivisions[divisionKey] = tempData.value.divisions[divisionKey];
  });

  tempData.value.divisions = newDivisions
  
};


function createTable(){
    data.value.divisions = tempData.value.divisions
}

function handlePrint(){
    print()
}
</script>

<template>
    <div class="no-print actions">
        <input type="file" ref="fileInput" @change="showUpload=true">
        <button v-if="showUpload" @click="uploadFile">Загрузить файл</button>
    </div>


<table class="no-print" v-if="tempData">
    <template v-for="(division, key) in tempData.divisions" :key="key">
        <tr>
            <td> {{ key }} </td>
            <td>
                <button @click="moveItem(key, 'up')" :disabled="isFirstDivision(key)">Up</button>
            </td>
            <td>
                <button @click="moveItem(key, 'down')" :disabled="isLastDivision(key)">Down</button>
            </td>
        </tr>
    </template>
</table>


<div class="no-print actions" v-if="data">
    <span>
        <button @click="createTable"> Cоздать таблицу </button>
    </span>
    <span>
        <button @click="handlePrint"> Печать </button>
    </span>
</div>


<table class="main-table" v-if="data != null">
    <tr class="main-table__title">
        <td> Отпуск - 2024</td>
    </tr>
    
    <tr>
        <table class="header-table">
            <tr>
                <td class="td-number"> № п/п </td>
                <td class="td-fio"> ФИО </td>
                <td>
                    <table class="table-months">
                        <tr class="table-months__header">
                            <template v-for="month, index in data.months">
                                    <td :colspan="data.months[0].weeks.length"> {{month.name}} </td>
                            </template>
                        </tr>
                            
                        <tr class="table-months__body">
                            <template v-for="month in data.months">
                                <template v-for="week in month.weeks">
                                    <td class="td-month-init"> <span class="vertical-text"> 
                                        {{ week[0] }}  
                                        <template v-if="week[1]"> {{ `-${week[1]}` }} </template>
                                    </span> </td>
                                </template>
                            </template>
                        </tr>
                    </table>
                </td>
                <td class="td-period"> Период </td>
                <td class="td-days"> Кол-во дней </td>
            </tr>
        </table>
    </tr>
    
    
    <template v-for="division, key in data.divisions">

        

        <tr class="main-table__title">
            <td> {{key}} </td> 
        </tr>


        <template v-for="employee in division">
            <tr class="data">
                <table class="data-table">
                    <tr>
                        <td class="td-number">{{division.indexOf(employee)+1}}</td>
                        <td class="td-fio">{{employee.ФИО}}</td>
                        
                        <td>
                            <table class="data-table__month-table">
                                <tr class="table-months__body">
                                    <template v-for="month, index_month in data.months">
                                        <template v-for="week, index_week in month.weeks">
                                            <td class="td-month-init td-month-init_employee "> 
                                                    <template v-for="vacation_with_weeks in employee.vacations_with_weeks">
                                                        <!-- one month vacation -->
                                                        <template v-if="vacation_with_weeks.start.month == vacation_with_weeks.end.month">
                                                            <!-- start -->
                                                            <template v-if="vacation_with_weeks.start.month == index_month">
                                                                <template v-if="vacation_with_weeks.start.week == index_week">
                                                                    <div class="vacation">
                                                                        {{ vacation_with_weeks.start.day }}
                                                                    </div>

                                                                </template>
                                                            </template>
                                                            <!-- medium -->
                                                            <template v-if="(vacation_with_weeks.start.month == index_month) && (vacation_with_weeks.start.week < index_week) && (vacation_with_weeks.end.week > index_week)">
                                                                <span class="vacation vertical-text">
                                                                    &nbsp; 
                                                                </span>
                                                            </template> 
                                                            <!-- end -->
                                                            <template v-if="vacation_with_weeks.end.month == index_month">
                                                                <template v-if="vacation_with_weeks.end.week == index_week">
                                                                    <span class="vacation">
                                                                        {{ vacation_with_weeks.end.day }}
                                                                    </span>
                                                                </template>
                                                            </template>
                                                        </template>

                                                        <!-- two months vacation -->
                                                        <template v-else-if="vacation_with_weeks.start.month != vacation_with_weeks.end.month">
                                                            <!-- start -->
                                                            <template v-if="vacation_with_weeks.start.month == index_month">
                                                                <template v-if="vacation_with_weeks.start.week == index_week">
                                                                    <span class="vacation ">
                                                                        {{ vacation_with_weeks.start.day }}
                                                                    </span>
                                                                </template>
                                                            </template>
                                                            <!-- medium -->
                                                            <template v-if="((vacation_with_weeks.start.month == index_month) && (vacation_with_weeks.start.week < index_week)) || 
                                                            ((vacation_with_weeks.end.month == index_month) && (vacation_with_weeks.end.week > index_week))">
                                                                <span class="vacation vertical-text">
                                                                    &nbsp;
                                                                </span>
                                                            </template> 
                                                            <!-- end -->
                                                            <template v-if="vacation_with_weeks.end.month == index_month">
                                                                <template v-if="vacation_with_weeks.end.week == index_week">
                                                                    <span class="vacation ">
                                                                        {{ vacation_with_weeks.end.day }}
                                                                    </span>
                                                                </template>
                                                            </template>
                                                        </template>
                                                    </template>
                                            </td>
                                        </template>
                                    </template>
                                </tr>
                            </table>
                        </td>
                        <td class="td-period">
                            <table class="data-table__period-table">
                                <template v-for="period in employee.отпуска">
                                    <tr>
                                        <td> {{ period["Дата с"].substring(0, period["Дата с"].length - 5) }}
                                            -
                                            {{ period["Дата по"].substring(0, period["Дата по"].length - 5)}}
                                            ({{ period["Кол-во дней"] }}дн)
                                            <span v-if="period['ЕСВ'].length !=0" > {{ period["ЕСВ"] }} </span> 
                                        </td>
                                    </tr>
                                </template>
                            </table>
                        </td>
                        <td class="td-days">{{ employee.дни }}</td>
                    </tr>
                </table>
            </tr>
        </template>

    </template>


</table>



</template>

<style lang="sass">
.actions
    padding: 1rem 0
    display: flex
    gap: 1rem0

.vacation
    display: table-cell
    vertical-align: middle
    height: 5rem
    width: 1.25rem 
    background: #bebebe
    // background: #ffb

.td-number
    min-width: 2rem
    width: 2rem
.td-fio
    min-width: 7rem
    width: 7rem
.td-month-init
    width: 20px
    min-width: 20px
    padding: 4px 0px !important
.td-period
    width: 13rem
    min-width: 13rem
.td-days
    width: 3rem
    min-width: 3rem

.data-table
    width: 100%  
    border-collapse: collapse
    td
        border: 1px solid
        text-align: center

    .data-table__month-table
        width: 100%  
        height: 70px
        td
            border: 0
        td
            padding: .5rem
            font-weight: 300
        td:not(:last-child)
            border-right: 1px solid
    .data-table__period-table
        border-collapse: collapse
        width: 100%
        td
            padding-left: .5rem
            border: none
            text-align: left

html
    font-size: 12px
    td
        padding: 0
.vertical-text
    writing-mode: vertical-lr
    transform: scale(-1)




.main-table, .header-table
    width: 100%  
    
.main-table
    border-collapse: collapse
    .main-table__title
        td
            text-align: center
            font-size: 16px
            font-weight: 600


.header-table
    text-align: center
    border-collapse: collapse
    td
        border: 1px solid
        font-weight: 600
    
.table-months
    width: 100%
    border-collapse: collapse
    td
        border: 0
        text-align: center
    .table-months__header
        font-weight: 600
        td
            border-bottom: 1px solid
        td:not(:last-child)
            border-right: 1px solid

    .table-months__body
        td
            padding: .5rem
            font-weight: 300
        td:not(:last-child)
            border-right: 1px solid

.td-month-init_employee
    padding: 0 !important
    height: 5rem !important

@media print 
    body 
        -webkit-print-color-adjust: exact
        print-color-adjust: exact
    .no-print
        display: none
</style>