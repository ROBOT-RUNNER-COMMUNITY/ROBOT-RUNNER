// This is the SIP interface definition for the QHash based mapped types
// specific to the QtCharts module.
//
// Copyright (c) 2025 Riverbank Computing Limited <info@riverbankcomputing.com>
// 
// This file is part of PyQt6-Charts.
// 
// This file may be used under the terms of the GNU General Public License
// version 3.0 as published by the Free Software Foundation and appearing in
// the file LICENSE included in the packaging of this file.  Please review the
// following information to ensure the GNU General Public License version 3.0
// requirements will be met: http://www.gnu.org/copyleft/gpl.html.
// 
// If you do not wish to use this file under the terms of the GPL version 3.0
// then you may purchase a commercial license.  For more information contact
// info@riverbankcomputing.com.
// 
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


%If (QtCharts_6_2_0 -)


%MappedType QHash<QXYSeries::PointConfiguration, QVariant>
        /TypeHint="Dict[QXYSeries.PointConfiguration, QVariant]",
        TypeHintValue="{}"/
{
%TypeHeaderCode
#include <qhash.h>
#include <qvariant.h>
#include <qxyseries.h>
%End

%ConvertFromTypeCode
    PyObject *d = PyDict_New();

    if (!d)
        return 0;

    QHash<QXYSeries::PointConfiguration, QVariant>::const_iterator it = sipCpp->constBegin();
    QHash<QXYSeries::PointConfiguration, QVariant>::const_iterator end = sipCpp->constEnd();

    while (it != end)
    {
        PyObject *kobj = sipConvertFromEnum(static_cast<int>(it.key()),
                sipType_QXYSeries_PointConfiguration);

        if (!kobj)
        {
            Py_DECREF(d);

            return 0;
        }

        QVariant *v = new QVariant(it.value());
        PyObject *vobj = sipConvertFromNewType(v, sipType_QVariant,
                sipTransferObj);

        if (!vobj)
        {
            delete v;
            Py_DECREF(kobj);
            Py_DECREF(d);

            return 0;
        }

        int rc = PyDict_SetItem(d, kobj, vobj);

        Py_DECREF(vobj);
        Py_DECREF(kobj);

        if (rc < 0)
        {
            Py_DECREF(d);

            return 0;
        }

        ++it;
    }

    return d;
%End

%ConvertToTypeCode
    if (!sipIsErr)
        return PyDict_Check(sipPy);

    QHash<QXYSeries::PointConfiguration, QVariant> *qh = new QHash<QXYSeries::PointConfiguration, QVariant>;

    Py_ssize_t pos = 0;
    PyObject *kobj, *vobj;
 
    while (PyDict_Next(sipPy, &pos, &kobj, &vobj))
    {
        int k = sipConvertToEnum(kobj, sipType_QXYSeries_PointConfiguration);

        if (PyErr_Occurred())
        {
            PyErr_Format(PyExc_TypeError,
                    "a key has type '%s' but 'QXYSeries.PointConfiguration' is expected",
                    sipPyTypeName(Py_TYPE(kobj)));

            delete qh;
            *sipIsErr = 1;

            return 0;
        }

        int vstate;
        QVariant *v = reinterpret_cast<QVariant *>(
                sipForceConvertToType(vobj, sipType_QVariant, sipTransferObj,
                        SIP_NOT_NONE, &vstate, sipIsErr));

        if (*sipIsErr)
        {
            // Any error must be internal, so leave the exception as it is.

            delete qh;

            return 0;
        }

        qh->insert(static_cast<QXYSeries::PointConfiguration>(k), *v);

        sipReleaseType(v, sipType_QVariant, vstate);
    }
 
    *sipCppPtr = qh;
 
    return sipGetState(sipTransferObj);
%End
};


%MappedType QHash<int, QHash<QXYSeries::PointConfiguration, QVariant> >
        /TypeHint="Dict[int, Dict[QXYSeries.PointConfiguration, QVariant]]",
        TypeHintValue="{}"/
{
%TypeHeaderCode
#include <qhash.h>
#include <qvariant.h>
#include <qxyseries.h>
%End

%ConvertFromTypeCode
    static const sipTypeDef *value_td = SIP_NULLPTR;

    if (!value_td)
    {
        value_td = sipFindType(
                "QHash<QXYSeries::PointConfiguration,QVariant>");
        Q_ASSERT(value_td);
    }

    PyObject *d = PyDict_New();

    if (!d)
        return 0;

    QHash<int, QHash<QXYSeries::PointConfiguration, QVariant> >::const_iterator it = sipCpp->constBegin();
    QHash<int, QHash<QXYSeries::PointConfiguration, QVariant> >::const_iterator end = sipCpp->constEnd();

    while (it != end)
    {
        PyObject *kobj = PyLong_FromLong(it.key());

        if (!kobj)
        {
            Py_DECREF(d);

            return 0;
        }

        QHash<QXYSeries::PointConfiguration, QVariant> v = it.value();
        PyObject *vobj = sipConvertFromType(&v, value_td, sipTransferObj);

        if (!vobj)
        {
            Py_DECREF(kobj);
            Py_DECREF(d);

            return 0;
        }

        int rc = PyDict_SetItem(d, kobj, vobj);

        Py_DECREF(vobj);
        Py_DECREF(kobj);

        if (rc < 0)
        {
            Py_DECREF(d);

            return 0;
        }

        ++it;
    }

    return d;
%End

%ConvertToTypeCode
    if (!sipIsErr)
        return PyDict_Check(sipPy);

    static const sipTypeDef *value_td = SIP_NULLPTR;

    if (!value_td)
    {
        value_td = sipFindType(
                "QHash<QXYSeries::PointConfiguration,QVariant>");
        Q_ASSERT(value_td);
    }

    QHash<int, QHash<QXYSeries::PointConfiguration, QVariant> > *qh = new QHash<int, QHash<QXYSeries::PointConfiguration, QVariant> >;

    Py_ssize_t pos = 0;
    PyObject *kobj, *vobj;
 
    while (PyDict_Next(sipPy, &pos, &kobj, &vobj))
    {
        int k = sipLong_AsInt(kobj);

        if (PyErr_Occurred())
        {
            PyErr_Format(PyExc_TypeError,
                    "a key has type '%s' but 'int' is expected",
                    sipPyTypeName(Py_TYPE(kobj)));

            delete qh;
            *sipIsErr = 1;

            return 0;
        }

        int vstate;
        QHash<QXYSeries::PointConfiguration, QVariant> *v = reinterpret_cast<QHash<QXYSeries::PointConfiguration, QVariant>*>(
                sipForceConvertToType(vobj, value_td, sipTransferObj,
                        SIP_NOT_NONE, &vstate, sipIsErr));

        if (*sipIsErr)
        {
            PyErr_Format(PyExc_TypeError,
                    "a dict value has type '%s' but 'dict' is expected",
                    sipPyTypeName(Py_TYPE(vobj)));

            delete qh;

            return 0;
        }

        qh->insert(k, *v);

        sipReleaseType(v, value_td, vstate);
    }
 
    *sipCppPtr = qh;
 
    return sipGetState(sipTransferObj);
%End
};


%End
