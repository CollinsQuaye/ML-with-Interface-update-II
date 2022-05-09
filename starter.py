import streamlit as st
import pandas as pd
import pickle
import io
import plotly.figure_factory as ff


##---------------------------------------------------------------------------------------------------------
## Edit logo and title of app
##---------------------------------------------------------------------------------------------------------
st.set_page_config(page_title='Steelwork Predictor', layout='centered', initial_sidebar_state='auto', menu_items=None)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('##')
with col2:
    st.image('Images/ML.png', width=250)
with col3:
    st.markdown('##')

st.markdown("<h4 style='font-family:Verdana;color:green;text-align:center;font-size:30px;'>Tilting Furnace Casting Steelwork Predictor</h4>", 
            unsafe_allow_html=True)

st.markdown('##')













##-----------------------------------------------------------------------------------------------------------------------------
## Page Layout - Focus Prediction
##----------------------------------------------------------------------------------------------------------------------------

with st.expander('Unit Casing Input', expanded=True):

    # take input from user for prediction
    form = st.form(key='my_form', clear_on_submit=True)
    capacity = form.number_input(label='Holding Capacity (Tonnes)', min_value=0, format="%d")
    door_height = form.number_input(label='Door Opening Height (mm)', min_value=0, format="%d")
    door_width = form.number_input(label='Door Opening Width (mm)', min_value=0, format="%d")
    metal_depth = form.number_input(label='Metal Bath Depth (mm)', min_value=0, format="%d")
    bath_length = form.number_input(label='Metal Bath Length (mm)', min_value=0, format="%d")
    form.markdown('##')
    submit_button = form.form_submit_button(label='Submit')

    # once user clicks on submit
    if submit_button:

        # get the data user inputted
        d = {'Holding C
             apacity (Tonnes)':[capacity], 'Door Opening Height (mm)':[door_height],'Door Opening Width (mm)': [door_width], 
            'Metal Bath Depth (mm)':[metal_depth], 'Metal Bath Length (mm)':[bath_length]}

        # create a dataframe and display it
        data = pd.DataFrame(data=d)
        d2 = {'Assembly Component': data.columns, 'Input Data':data.iloc[0]}
        new_data = pd.DataFrame(data=d2)
        new_data.set_index('Assembly Component', inplace=True)

        st.markdown('##')

        # data visualization in table form
        st.markdown("<p style='color:green; font-family:Verdana;'>Input Data</p>", unsafe_allow_html=True)
        fig = ff.create_table(new_data, colorscale=[[0, '#6EB52F'], [.5, '#e5fddc'],[1, '#ffffff']], index=True, index_title='Assembly Components')
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 18

        st.plotly_chart(fig, use_container_width=True)


        st.markdown('##')

        # load the trained model
        st.markdown("<p style='color:green; font-family:Verdana;'>Predicted Output</p>", unsafe_allow_html=True)
        def pred_model(model):
            with open(model, 'rb') as f:
                model = pickle.load(f)

            # define names for columns
            pred_columns = ['Hearth Back Ramp', 'Hearth Centre Base', 'Hearth Front Ramp', 'Back Wall', 'Left Wall','Right Wall', 'Roof Beams', 
            'Lintel Beam', 'Overhead Door Shaft','Door Fabrication', 'Heat Shield', 'Door Surround Casting','Refractory', 'Total Casing Steelwork']
            
            # make prediction and round values to 0 decimal places
            y_pred = model.predict(data)
    
            output_df = pd.DataFrame(y_pred, columns=pred_columns)
            
            d3 = {'Assembly Component': output_df.columns, 'Predicted Weight (Kgs)': output_df.iloc[0]}

            final = pd.DataFrame(data=d3)
            final['Predicted Weight (Kgs)'] = final['Predicted Weight (Kgs)'].abs().astype('int')
            final.set_index('Assembly Component', inplace=True)
            
            return final

        # display predicted output
        pred_data = pred_model('./final_model.pkl')

        # data visualization
        fig = ff.create_table(pred_data, colorscale=[[0, '#6EB52F'], [.5, '#e5fddc'],[1, '#ffffff']], index=True, index_title='Assembly Components')
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 18
        
        st.plotly_chart(fig, use_container_width=True)












st.markdown('##')
##-----------------------------------------------------------------------------------------------------------------------------
## Page Layout - Batch Prediction
##----------------------------------------------------------------------------------------------------------------------------

with st.expander('Batch Prediction'):

    # define the file uploader
    def file_upload(name):
            uploaded_file = st.file_uploader('%s' % (name),key='%s' % (name), accept_multiple_files=False)
            content = False
            if uploaded_file is not None:
                try:
                    uploaded_df = pd.read_csv(uploaded_file)
                    content = True
                    return content, uploaded_df
                except:
                    try:
                        uploaded_df = pd.read_excel(uploaded_file)
                        content = True
                        return content, uploaded_df
                    except:
                        st.error('Please ensure file is .csv or .xlsx format and/or reupload file')
                        return content, None
            else:
                return content, None

    st.markdown('##')

    # define template file to be uploaded
    st.markdown("<p style='color:green; font-family: Verdana; font-size:1em;'>Please upload batch input data for steelwork prediction.\
                    See template below (.xlsx or .csv)</p>", unsafe_allow_html=True)
    st.write(' ')
    st.image('Images/template.png')

    # upload file in csv or excel format
    status, df = file_upload(" ")

    st.markdown('##')

    # once user clicks submit
    if st.button('Submit'):

        # make prediction
        def pred_model(model):
            with open(model , 'rb') as f:
                model = pickle.load(f)

            # define names of columns
            pred_columns = ['Hearth Back Ramp', 'Hearth Centre Base', 'Hearth Front Ramp', 'Back Wall', 'Left Wall','Right Wall', 'Roof Beams', 
            'Lintel Beam', 'Overhead Door Shaft','Door Fabrication', 'Heat Shield', 'Door Surround Casting','Refractory', 'Total Casing Steelwork']
            
            # make predictions and round to zero decimal places
            y_pred = model.predict(df)
            output_df = pd.DataFrame(y_pred, columns=pred_columns)
            output_df = output_df.abs().astype('int')
            
            # join input data to output data
            result = pd.concat([df, output_df], axis=1, join='inner')

            # set custom index range for dataframe
            new_index = [str(i).zfill(6) for i in range(1, result.shape[0]+1)]
            result.index = new_index

            return result
        
        st.markdown('##')

        # make predictions and display output
        st.markdown("<p style='color:green; font-family: Verdana;'>Predicted Output</p>", unsafe_allow_html=True)
        pred_data = pred_model('./final_model.pkl')
        st.dataframe(pred_data)

        st.markdown('##')

        # user can download data here - remember to 'pip install xlsxwriter'
        name = 'steelwork' + '.xlsx'

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pred_data.to_excel(writer, index=True)
            writer.save()

        st.download_button(label='Download Data', data=buffer, file_name=name, mime='application/vnd.ms-excel')

        
        

